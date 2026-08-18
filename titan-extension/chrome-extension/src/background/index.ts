import 'webextension-polyfill';
import {
  agentModelStore,
  AgentNameEnum,
  firewallStore,
  generalSettingsStore,
  llmProviderStore,
  analyticsSettingsStore,
} from '@extension/storage';
import { t } from '@extension/i18n';
import BrowserContext from './browser/context';
import { Executor } from './agent/executor';
import { createLogger } from './log';
import { ExecutionState } from './agent/event/types';
import { createChatModel } from './agent/helper';
import type { BaseChatModel } from '@langchain/core/language_models/chat_models';
import { DEFAULT_AGENT_OPTIONS } from './agent/types';
import { SpeechToTextService } from './services/speechToText';
import { injectBuildDomTreeScripts } from './browser/dom/service';
import { analytics } from './services/analytics';

const logger = createLogger('background');

const browserContext = new BrowserContext({});
let currentExecutor: Executor | null = null;
let currentPort: chrome.runtime.Port | null = null;
const SIDE_PANEL_URL = chrome.runtime.getURL('side-panel/index.html');

// --- SHADOW-LINK PC BRIDGE ---
function notifySidePanel(data: any) {
  try {
    if (currentPort) {
      currentPort.postMessage(data);
    }
  } catch {
    // ignore
  }
}

let pingIntervalId: any = null;

function connectToShadowPC() {
    if (pingIntervalId) {
        clearInterval(pingIntervalId);
        pingIntervalId = null;
    }

    const ws = new WebSocket('ws://127.0.0.1:8002');
    
    ws.onopen = () => {
        logger.info('🛰️ Connected to Shadow-PC Master Brain');
        notifySidePanel({ type: 'bridge_event', status: 'connected', text: '🛰️ Connected to TITAN Master Brain (ws://127.0.0.1:8002)' });
        
        // Keepalive heartbeat every 10s to prevent MV3 worker sleep
        pingIntervalId = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'ping' }));
            }
        }, 10000);
    };

    ws.onmessage = async (event) => {
        let message: any;
        try {
            message = JSON.parse(event.data);
        } catch {
            return;
        }

        if (message.type === 'pong' || message.type === 'ping') {
            return;
        }

        logger.info('📥 Received Remote Task:', message);
        notifySidePanel({ type: 'bridge_event', status: 'cmd_received', text: `📥 [RECV] ${message.action || message.type || 'task'} ${JSON.stringify(message.url || message.text || message.task || '')}` });

        if (message.type === 'action') {
            try {
                const action = message.action;
                const page = await browserContext.getCurrentPage();
                
                if (!page) {
                    ws.send(JSON.stringify({
                        id: message.id,
                        state: 'ERROR',
                        msg: 'No active page context found'
                    }));
                    notifySidePanel({ type: 'bridge_event', status: 'cmd_error', text: '❌ No active page context found' });
                    return;
                }

                let resultMsg = '';

                switch (action) {
                    case 'get_url': {
                        const browserState = await browserContext.getState(false);
                        ws.send(JSON.stringify({
                            id: message.id,
                            state: 'COMPLETE',
                            result: {
                                url: browserState.url,
                                title: browserState.title
                            }
                        }));
                        notifySidePanel({ type: 'bridge_event', status: 'cmd_done', text: `📤 [URL] "${browserState.title}" (${browserState.url})` });
                        return;
                    }
                    case 'extract': {
                        const browserState = await browserContext.getState(true);
                        const elementsText = browserState.elementTree.clickableElementsToString(
                            DEFAULT_AGENT_OPTIONS.includeAttributes
                        );
                        ws.send(JSON.stringify({
                            id: message.id,
                            state: 'COMPLETE',
                            result: {
                                url: browserState.url,
                                title: browserState.title,
                                text: elementsText
                            }
                        }));
                        notifySidePanel({ type: 'bridge_event', status: 'cmd_done', text: `📤 [EXTRACT] Extracted content from "${browserState.title}"` });
                        return;
                    }
                    case 'navigate': {
                        if (!message.url) throw new Error('url is required');
                        await browserContext.navigateTo(message.url);
                        resultMsg = `Navigated to ${message.url}`;
                        break;
                    }
                    case 'get_state': {
                        const browserState = await browserContext.getState(true);
                        const elementsText = browserState.elementTree.clickableElementsToString(
                            DEFAULT_AGENT_OPTIONS.includeAttributes
                        );
                        ws.send(JSON.stringify({
                            id: message.id,
                            state: 'COMPLETE',
                            result: {
                                url: browserState.url,
                                title: browserState.title,
                                interactive_elements: elementsText,
                                tabs: browserState.tabs
                            }
                        }));
                        notifySidePanel({ type: 'bridge_event', status: 'cmd_done', text: `📤 [STATE] Extracted DOM tree for "${browserState.title}" (${browserState.url})` });
                        return;
                    }
                    case 'click': {
                        if (message.index === undefined) throw new Error('index is required');
                        const elementNode = page.getDomElementByIndex(message.index);
                        if (!elementNode) throw new Error(`Element at index ${message.index} not found. Run get_state first.`);
                        await page.clickElementNode(false, elementNode);
                        resultMsg = `Clicked element at index ${message.index}`;
                        break;
                    }
                    case 'input': {
                        if (message.index === undefined || message.text === undefined) {
                            throw new Error('index and text are required');
                        }
                        const elementNode = page.getDomElementByIndex(message.index);
                        if (!elementNode) throw new Error(`Element at index ${message.index} not found. Run get_state first.`);
                        await page.inputTextElementNode(false, elementNode, message.text);
                        resultMsg = `Typed "${message.text}" into element [${message.index}]`;
                        break;
                    }
                    case 'back': {
                        await page.goBack();
                        resultMsg = 'Navigated back';
                        break;
                    }
                    case 'forward': {
                        await page.goForward();
                        resultMsg = 'Navigated forward';
                        break;
                    }
                    case 'refresh': {
                        await page.refreshPage();
                        resultMsg = 'Refreshed page';
                        break;
                    }
                    case 'scroll_down': {
                        const amount = message.amount || 500;
                        await page.scrollBy(amount);
                        resultMsg = `Scrolled down by ${amount}px`;
                        break;
                    }
                    case 'scroll_up': {
                        const amount = message.amount || 500;
                        await page.scrollBy(-amount);
                        resultMsg = `Scrolled up by ${amount}px`;
                        break;
                    }
                    case 'scroll_to_text': {
                        if (!message.text) throw new Error('text is required');
                        const ok = await page.scrollToText(message.text);
                        resultMsg = ok ? `Scrolled to text "${message.text}"` : `Text "${message.text}" not found on page`;
                        break;
                    }
                    case 'get_dropdown_options': {
                        if (message.index === undefined) throw new Error('index is required');
                        const options = await page.getDropdownOptions(message.index);
                        ws.send(JSON.stringify({
                            id: message.id,
                            state: 'COMPLETE',
                            result: { options }
                        }));
                        notifySidePanel({ type: 'bridge_event', status: 'cmd_done', text: `📤 [DROPDOWN] Retrieved ${options?.length || 0} options` });
                        return;
                    }
                    case 'select_dropdown': {
                        if (message.index === undefined || !message.text) {
                            throw new Error('index and text are required');
                        }
                        const msg = await page.selectDropdownOption(message.index, message.text);
                        resultMsg = msg;
                        break;
                    }
                    case 'send_keys': {
                        if (!message.keys) throw new Error('keys are required');
                        await page.sendKeys(message.keys);
                        resultMsg = `Sent keys ${message.keys}`;
                        break;
                    }
                    case 'screenshot': {
                        const screenshot = await page.takeScreenshot();
                        ws.send(JSON.stringify({
                            id: message.id,
                            state: 'COMPLETE',
                            result: { screenshot }
                        }));
                        notifySidePanel({ type: 'bridge_event', status: 'cmd_done', text: '📤 [SCREENSHOT] Captured full tab screenshot' });
                        return;
                    }
                    case 'open_tab': {
                        if (!message.url) throw new Error('url is required');
                        await browserContext.openTab(message.url);
                        resultMsg = `Opened new tab: ${message.url}`;
                        break;
                    }
                    case 'close_tab': {
                        const activePage = await browserContext.getCurrentPage();
                        if (activePage) {
                            await browserContext.closeTab(activePage.tabId);
                            resultMsg = 'Closed current tab';
                        } else {
                            throw new Error('No active page context to close');
                        }
                        break;
                    }
                    case 'switch_tab': {
                        if (message.tab_id === undefined) throw new Error('tab_id is required');
                        await browserContext.switchTab(message.tab_id);
                        resultMsg = `Switched to tab ${message.tab_id}`;
                        break;
                    }
                    default: {
                        throw new Error(`Unknown action: ${action}`);
                    }
                }

                ws.send(JSON.stringify({
                    id: message.id,
                    state: 'COMPLETE',
                    result: { msg: resultMsg }
                }));
                notifySidePanel({ type: 'bridge_event', status: 'cmd_done', text: `📤 [DONE] ${resultMsg}` });

            } catch (error: any) {
                const errMsg = error.message || 'Unknown error';
                ws.send(JSON.stringify({
                    id: message.id,
                    state: 'ERROR',
                    msg: errMsg
                }));
                notifySidePanel({ type: 'bridge_event', status: 'cmd_error', text: `❌ [ERROR] ${errMsg}` });
            }
        } else if (message.type === 'new_task') {
            const [tab] = await chrome.tabs.query({ active: true, lastFocusedWindow: true });
            if (!tab || !tab.id) {
                ws.send(JSON.stringify({state: 'ERROR', msg: 'No active tab found'}));
                notifySidePanel({ type: 'bridge_event', status: 'cmd_error', text: '❌ No active tab found for task' });
                return;
            }

            try {
                notifySidePanel({ type: 'bridge_event', status: 'task_started', text: `⚡ [TASK START] ${message.task}` });
                currentExecutor = await setupExecutor(message.taskId, message.task, browserContext);
                subscribeToExecutorEvents(currentExecutor);
                
                currentExecutor.subscribeExecutionEvents(async event => {
                    ws.send(JSON.stringify(event));
                    if (event.data?.details) {
                        notifySidePanel({ type: 'bridge_event', status: 'agent_step', text: `🤖 [${event.actor}] ${event.data.details}` });
                    }
                });

                const result = await currentExecutor.execute();
                ws.send(JSON.stringify({state: 'COMPLETE', result}));
                notifySidePanel({ type: 'bridge_event', status: 'task_done', text: '✅ [TASK COMPLETE] Finished autonomous execution.' });
            } catch (error: any) {
                ws.send(JSON.stringify({state: 'ERROR', msg: error.message}));
                notifySidePanel({ type: 'bridge_event', status: 'cmd_error', text: `❌ [TASK FAILED] ${error.message}` });
            }
        }
    };

    ws.onclose = () => {
        if (pingIntervalId) {
            clearInterval(pingIntervalId);
            pingIntervalId = null;
        }
        logger.warning('⚠️ Shadow-PC Connection Lost. Retrying in 2s...');
        notifySidePanel({ type: 'bridge_event', status: 'disconnected', text: '⚠️ Disconnected from TITAN Master Brain. Retrying in 2s...' });
        setTimeout(connectToShadowPC, 2000);
    };
}

connectToShadowPC();
// -----------------------------

// Setup side panel behavior
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(error => console.error(error));

chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
  if (tabId && changeInfo.status === 'complete' && tab.url?.startsWith('http')) {
    await injectBuildDomTreeScripts(tabId);
  }
});

// Listen for debugger detached event
// if canceled_by_user, remove the tab from the browser context
chrome.debugger.onDetach.addListener(async (source, reason) => {
  console.log('Debugger detached:', source, reason);
  if (reason === 'canceled_by_user') {
    if (source.tabId) {
      currentExecutor?.cancel();
      await browserContext.cleanup();
    }
  }
});

// Cleanup when tab is closed
chrome.tabs.onRemoved.addListener(tabId => {
  browserContext.removeAttachedPage(tabId);
});

logger.info('background loaded');

// Initialize analytics
analytics.init().catch(error => {
  logger.error('Failed to initialize analytics:', error);
});

// Listen for analytics settings changes
analyticsSettingsStore.subscribe(() => {
  analytics.updateSettings().catch(error => {
    logger.error('Failed to update analytics settings:', error);
  });
});

// Listen for simple messages (e.g., from options page)
chrome.runtime.onMessage.addListener(() => {
  // Handle other message types if needed in the future
  // Return false if response is not sent asynchronously
  // return false;
});

// Setup connection listener for long-lived connections (e.g., side panel)
chrome.runtime.onConnect.addListener(port => {
  if (port.name === 'side-panel-connection') {
    const senderUrl = port.sender?.url;
    const senderId = port.sender?.id;

    if (!senderUrl || senderId !== chrome.runtime.id || senderUrl !== SIDE_PANEL_URL) {
      logger.warning('Blocked unauthorized side-panel-connection', senderId, senderUrl);
      port.disconnect();
      return;
    }

    currentPort = port;

    port.onMessage.addListener(async message => {
      try {
        switch (message.type) {
          case 'heartbeat':
            // Acknowledge heartbeat
            port.postMessage({ type: 'heartbeat_ack' });
            break;

          case 'new_task': {
            if (!message.task) return port.postMessage({ type: 'error', error: t('bg_cmd_newTask_noTask') });
            if (!message.tabId) return port.postMessage({ type: 'error', error: t('bg_errors_noTabId') });

            logger.info('new_task', message.tabId, message.task);
            currentExecutor = await setupExecutor(message.taskId, message.task, browserContext);
            subscribeToExecutorEvents(currentExecutor);

            const result = await currentExecutor.execute();
            logger.info('new_task execution result', message.tabId, result);
            break;
          }

          case 'follow_up_task': {
            if (!message.task) return port.postMessage({ type: 'error', error: t('bg_cmd_followUpTask_noTask') });
            if (!message.tabId) return port.postMessage({ type: 'error', error: t('bg_errors_noTabId') });

            logger.info('follow_up_task', message.tabId, message.task);

            // If executor exists, add follow-up task
            if (currentExecutor) {
              currentExecutor.addFollowUpTask(message.task);
              // Re-subscribe to events in case the previous subscription was cleaned up
              subscribeToExecutorEvents(currentExecutor);
              const result = await currentExecutor.execute();
              logger.info('follow_up_task execution result', message.tabId, result);
            } else {
              // executor was cleaned up, can not add follow-up task
              logger.info('follow_up_task: executor was cleaned up, can not add follow-up task');
              return port.postMessage({ type: 'error', error: t('bg_cmd_followUpTask_cleaned') });
            }
            break;
          }

          case 'cancel_task': {
            if (!currentExecutor) return port.postMessage({ type: 'error', error: t('bg_errors_noRunningTask') });
            await currentExecutor.cancel();
            break;
          }

          case 'resume_task': {
            if (!currentExecutor) return port.postMessage({ type: 'error', error: t('bg_cmd_resumeTask_noTask') });
            await currentExecutor.resume();
            return port.postMessage({ type: 'success' });
          }

          case 'pause_task': {
            if (!currentExecutor) return port.postMessage({ type: 'error', error: t('bg_errors_noRunningTask') });
            await currentExecutor.pause();
            return port.postMessage({ type: 'success' });
          }

          case 'screenshot': {
            if (!message.tabId) return port.postMessage({ type: 'error', error: t('bg_errors_noTabId') });
            const page = await browserContext.switchTab(message.tabId);
            const screenshot = await page.takeScreenshot();
            logger.info('screenshot', message.tabId, screenshot);
            return port.postMessage({ type: 'success', screenshot });
          }

          case 'state': {
            try {
              const browserState = await browserContext.getState(true);
              const elementsText = browserState.elementTree.clickableElementsToString(
                DEFAULT_AGENT_OPTIONS.includeAttributes,
              );

              logger.info('state', browserState);
              logger.info('interactive elements', elementsText);
              return port.postMessage({ type: 'success', msg: t('bg_cmd_state_printed') });
            } catch (error) {
              logger.error('Failed to get state:', error);
              return port.postMessage({ type: 'error', error: t('bg_cmd_state_failed') });
            }
          }

          case 'nohighlight': {
            const page = await browserContext.getCurrentPage();
            await page.removeHighlight();
            return port.postMessage({ type: 'success', msg: t('bg_cmd_nohighlight_ok') });
          }

          case 'speech_to_text': {
            try {
              if (!message.audio) {
                return port.postMessage({
                  type: 'speech_to_text_error',
                  error: t('bg_cmd_stt_noAudioData'),
                });
              }

              logger.info('Processing speech-to-text request...');

              // Get all providers for speech-to-text service
              const providers = await llmProviderStore.getAllProviders();

              // Create speech-to-text service with all providers
              const speechToTextService = await SpeechToTextService.create(providers);

              // Extract base64 audio data (remove data URL prefix if present)
              let base64Audio = message.audio;
              if (base64Audio.startsWith('data:')) {
                base64Audio = base64Audio.split(',')[1];
              }

              // Transcribe audio
              const transcribedText = await speechToTextService.transcribeAudio(base64Audio);

              logger.info('Speech-to-text completed successfully');
              return port.postMessage({
                type: 'speech_to_text_result',
                text: transcribedText,
              });
            } catch (error) {
              logger.error('Speech-to-text failed:', error);
              return port.postMessage({
                type: 'speech_to_text_error',
                error: error instanceof Error ? error.message : t('bg_cmd_stt_failed'),
              });
            }
          }

          case 'replay': {
            if (!message.tabId) return port.postMessage({ type: 'error', error: t('bg_errors_noTabId') });
            if (!message.taskId) return port.postMessage({ type: 'error', error: t('bg_errors_noTaskId') });
            if (!message.historySessionId)
              return port.postMessage({ type: 'error', error: t('bg_cmd_replay_noHistory') });
            logger.info('replay', message.tabId, message.taskId, message.historySessionId);

            try {
              // Switch to the specified tab
              await browserContext.switchTab(message.tabId);
              // Setup executor with the new taskId and a dummy task description
              currentExecutor = await setupExecutor(message.taskId, message.task, browserContext);
              subscribeToExecutorEvents(currentExecutor);

              // Run replayHistory with the history session ID
              const result = await currentExecutor.replayHistory(message.historySessionId);
              logger.debug('replay execution result', message.tabId, result);
            } catch (error) {
              logger.error('Replay failed:', error);
              return port.postMessage({
                type: 'error',
                error: error instanceof Error ? error.message : t('bg_cmd_replay_failed'),
              });
            }
            break;
          }

          default:
            return port.postMessage({ type: 'error', error: t('errors_cmd_unknown', [message.type]) });
        }
      } catch (error) {
        console.error('Error handling port message:', error);
        port.postMessage({
          type: 'error',
          error: error instanceof Error ? error.message : t('errors_unknown'),
        });
      }
    });

    port.onDisconnect.addListener(() => {
      // this event is also triggered when the side panel is closed, so we need to cancel the task
      console.log('Side panel disconnected');
      currentPort = null;
      currentExecutor?.cancel();
    });
  }
});

async function setupExecutor(taskId: string, task: string, browserContext: BrowserContext) {
  const providers = await llmProviderStore.getAllProviders();
  // if no providers, need to display the options page
  if (Object.keys(providers).length === 0) {
    throw new Error(t('bg_setup_noApiKeys'));
  }

  // Clean up any legacy validator settings for backward compatibility
  await agentModelStore.cleanupLegacyValidatorSettings();

  const agentModels = await agentModelStore.getAllAgentModels();
  // verify if every provider used in the agent models exists in the providers
  for (const agentModel of Object.values(agentModels)) {
    if (!providers[agentModel.provider]) {
      throw new Error(t('bg_setup_noProvider', [agentModel.provider]));
    }
  }

  const navigatorModel = agentModels[AgentNameEnum.Navigator];
  if (!navigatorModel) {
    throw new Error(t('bg_setup_noNavigatorModel'));
  }
  // Log the provider config being used for the navigator
  const navigatorProviderConfig = providers[navigatorModel.provider];
  const navigatorLLM = createChatModel(navigatorProviderConfig, navigatorModel);

  let plannerLLM: BaseChatModel | null = null;
  const plannerModel = agentModels[AgentNameEnum.Planner];
  if (plannerModel) {
    // Log the provider config being used for the planner
    const plannerProviderConfig = providers[plannerModel.provider];
    plannerLLM = createChatModel(plannerProviderConfig, plannerModel);
  }

  // Apply firewall settings to browser context
  const firewall = await firewallStore.getFirewall();
  if (firewall.enabled) {
    browserContext.updateConfig({
      allowedUrls: firewall.allowList,
      deniedUrls: firewall.denyList,
    });
  } else {
    browserContext.updateConfig({
      allowedUrls: [],
      deniedUrls: [],
    });
  }

  const generalSettings = await generalSettingsStore.getSettings();
  browserContext.updateConfig({
    minimumWaitPageLoadTime: generalSettings.minWaitPageLoad / 1000.0,
    displayHighlights: generalSettings.displayHighlights,
  });

  const executor = new Executor(task, taskId, browserContext, navigatorLLM, {
    plannerLLM: plannerLLM ?? navigatorLLM,
    agentOptions: {
      maxSteps: generalSettings.maxSteps,
      maxFailures: generalSettings.maxFailures,
      maxActionsPerStep: generalSettings.maxActionsPerStep,
      useVision: generalSettings.useVision,
      useVisionForPlanner: true,
      planningInterval: generalSettings.planningInterval,
    },
    generalSettings: generalSettings,
  });

  return executor;
}

// Update subscribeToExecutorEvents to use port
async function subscribeToExecutorEvents(executor: Executor) {
  // Clear previous event listeners to prevent multiple subscriptions
  executor.clearExecutionEvents();

  // Subscribe to new events
  executor.subscribeExecutionEvents(async event => {
    try {
      if (currentPort) {
        currentPort.postMessage(event);
      }
    } catch (error) {
      logger.error('Failed to send message to side panel:', error);
    }

    if (
      event.state === ExecutionState.TASK_OK ||
      event.state === ExecutionState.TASK_FAIL ||
      event.state === ExecutionState.TASK_CANCEL
    ) {
      await currentExecutor?.cleanup();
    }
  });
}
