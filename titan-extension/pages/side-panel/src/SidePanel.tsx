/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback, useRef } from 'react';
import { FiTrash2 } from 'react-icons/fi';
import './SidePanel.css';

declare global {
  interface Window {
    chrome: typeof chrome;
  }
}

interface LogEntry {
  id: string;
  type: 'info' | 'recv' | 'done' | 'error';
  text: string;
  timestamp: string;
}

const SidePanel = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: 'init-1',
      type: 'info',
      text: '⚡ TITAN Browser Link Monitor Initialized (ws://localhost:8002)',
      timestamp: new Date().toLocaleTimeString(),
    },
  ]);

  const portRef = useRef<chrome.runtime.Port | null>(null);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const addLog = useCallback((type: 'info' | 'recv' | 'done' | 'error', text: string) => {
    if (!text || !text.trim()) return;
    setLogs(prev => [
      ...prev,
      {
        id: `${Date.now()}-${Math.random()}`,
        type,
        text: text.trim(),
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
      },
    ]);
  }, []);

  // Scroll to bottom on new log
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Connect to Chrome runtime port to listen for background bridge events
  const connectPort = useCallback(() => {
    if (portRef.current) return;
    try {
      const port = chrome.runtime.connect({ name: 'side-panel-connection' });
      port.onMessage.addListener(msg => {
        if (msg?.type === 'bridge_event') {
          if (msg.status === 'connected') {
            setIsConnected(true);
            addLog('info', msg.text || 'Connected to TITAN Master Brain');
          } else if (msg.status === 'disconnected') {
            setIsConnected(false);
            addLog('error', msg.text || 'Disconnected from TITAN Master Brain');
          } else if (msg.status === 'cmd_received') {
            addLog('recv', msg.text || 'Command received');
          } else if (msg.status === 'cmd_done' || msg.status === 'task_done') {
            addLog('done', msg.text || 'Command executed');
          } else if (msg.status === 'cmd_error') {
            addLog('error', msg.text || 'Command error');
          } else {
            addLog('info', msg.text || JSON.stringify(msg));
          }
        }
      });
      port.onDisconnect.addListener(() => {
        portRef.current = null;
        setIsConnected(false);
      });
      portRef.current = port;
    } catch (e: any) {
      addLog('error', `Connection error: ${e.message}`);
    }
  }, [addLog]);

  useEffect(() => {
    connectPort();
    return () => {
      portRef.current?.disconnect();
      portRef.current = null;
    };
  }, [connectPort]);

  const handleClear = () => {
    setLogs([
      {
        id: `clear-${Date.now()}`,
        type: 'info',
        text: 'Screen cleared. Monitoring active.',
        timestamp: new Date().toLocaleTimeString(),
      },
    ]);
  };

  return (
    <div className="flex h-screen w-full flex-col bg-zinc-950 text-zinc-100 font-mono select-text">
      {/* Header with Connection Status */}
      <div className="flex items-center justify-between border-b border-zinc-800 bg-zinc-900 px-3 py-2 text-xs">
        <div className="flex items-center gap-2 font-semibold">
          <span className={`size-2.5 rounded-full ${isConnected ? 'bg-emerald-500 animate-pulse' : 'bg-amber-500'}`}></span>
          <span className="tracking-wide">TITAN LINK</span>
          <span className="text-zinc-500 font-normal">
            ({isConnected ? 'CONNECTED: 8002' : 'CONNECTING...'})
          </span>
        </div>
        <button
          onClick={handleClear}
          className="flex items-center gap-1 rounded bg-zinc-800 hover:bg-zinc-700 px-2 py-1 text-zinc-300 transition-colors cursor-pointer"
          title="Clear Screen">
          <FiTrash2 size={12} />
          <span>Clear</span>
        </button>
      </div>

      {/* Live Command & Response Feed */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2 text-xs leading-relaxed">
        {logs.map(log => (
          <div
            key={log.id}
            className={`p-2 rounded border ${
              log.type === 'recv'
                ? 'border-blue-900/60 bg-blue-950/40 text-blue-200'
                : log.type === 'done'
                  ? 'border-emerald-900/60 bg-emerald-950/40 text-emerald-200'
                  : log.type === 'error'
                    ? 'border-rose-900/60 bg-rose-950/40 text-rose-200'
                    : 'border-zinc-800 bg-zinc-900 text-zinc-300'
            }`}>
            <div className="flex justify-between items-center text-[10px] text-zinc-500 mb-1">
              <span className="uppercase font-semibold tracking-wider">
                {log.type === 'recv' ? '📥 COMMAND' : log.type === 'done' ? '📤 RESPONSE' : log.type === 'error' ? '❌ ERROR' : '⚡ SYSTEM'}
              </span>
              <span>{log.timestamp}</span>
            </div>
            <div className="whitespace-pre-wrap break-words">{log.text}</div>
          </div>
        ))}
        <div ref={logsEndRef} />
      </div>

      {/* Bottom Status Bar */}
      <div className="border-t border-zinc-800 bg-zinc-900 px-3 py-1.5 text-[11px] text-zinc-400 flex justify-between items-center">
        <span>Listening for TITAN commands...</span>
        <span className="text-zinc-500">{logs.length} events</span>
      </div>
    </div>
  );
};

export default SidePanel;
