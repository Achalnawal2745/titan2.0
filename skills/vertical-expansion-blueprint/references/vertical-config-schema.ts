/**
 * Vertical Roleplay Platform Configuration Schema
 * 
 * This TypeScript interface defines the configuration structure for deploying
 * AI roleplay training platforms across ANY vertical industry.
 * 
 * Usage: Create a JSON file matching this schema, run the generator, get a full platform.
 */

export interface VerticalConfig {
  /**
   * Metadata about this vertical configuration
   */
  metadata: {
    /** Unique identifier for this vertical (e.g., "sales", "dating", "therapy") */
    id: string;
    /** Human-readable name (e.g., "Door-to-Door Sales Training") */
    name: string;
    /** Brief description of the training platform */
    description: string;
    /** Version of this config */
    version: string;
    /** Author/creator of this config */
    author: string;
  };

  /**
   * Domain-specific context that defines the training scenario
   */
  domain: {
    /** What industry/context is this? (e.g., "Door-to-door fiber internet sales") */
    name: string;
    /** What role is the trainee playing? (e.g., "Sales rep", "Person approaching", "Therapist") */
    traineeRole: string;
    /** What role is the AI playing? (e.g., "Homeowner", "Potential romantic interest", "Client") */
    aiRole: string;
    /** What is the goal of each session? (e.g., "Close the sale", "Get phone number", "Build rapport") */
    goal: string;
    /** Optional: Industry-specific context or background */
    context?: string;
  };

  /**
   * AI Persona System: 4 distinct personality archetypes
   * 
   * Each persona represents a different challenge/approach for the trainee.
   * Pattern: Always 4 personas per vertical for consistency.
   */
  personas: Array<{
    /** Unique identifier (e.g., "lamb", "bull", "tiger", "owl") */
    id: string;
    /** Display name (e.g., "Lamb", "Bull", "Tiger", "Owl") */
    name: string;
    /** Emoji or icon to represent this persona */
    emoji: string;
    /** Short personality description (1-2 sentences) */
    description: string;
    /** Full personality traits for AI prompt */
    traits: string;
    /** 4 concrete response examples that match this personality */
    responseExamples: string[];
    /** How this persona raises objections (style description) */
    objectionStyle: string;
  }>;

  /**
   * Difficulty Progression System: 5 graduated challenge levels
   * 
   * Each level has explicit behavioral parameters (not vague descriptions).
   * Pattern: Always 5 levels (Rookie, Intermediate, Advanced, Expert, Nightmare)
   */
  difficultyLevels: Array<{
    /** Unique identifier (e.g., "rookie", "intermediate", "advanced", "expert", "nightmare") */
    id: string;
    /** Display name (e.g., "Rookie", "Intermediate", "Advanced", "Expert", "Nightmare") */
    name: string;
    /** Short description for UI */
    description: string;
    /** Explicit behavioral parameters */
    parameters: {
      /** How many exchanges before AI is ready to close/complete goal? */
      turnsToClose: { min: number; max: number };
      /** How many objections will AI raise? */
      objectionCount: { min: number; max: number };
      /** How long does AI pause between responses? (seconds) */
      pauseLength: { min: number; max: number };
      /** What percentage of responses are ultra-short (1-3 words)? */
      minimalResponseRate: number; // 0-100
    };
    /** Full difficulty modifier text for AI prompt */
    promptModifier: string;
  }>;

  /**
   * Practice Mode System: 5-7 focused training scenarios
   * 
   * Each mode isolates a specific skill within the vertical.
   * Pattern: 5-7 modes per vertical, each with clear focus.
   */
  practiceModes: Array<{
    /** Unique identifier (e.g., "full_pitch", "opener_only", "objection_handling") */
    id: string;
    /** Display name (e.g., "Full Pitch", "Opener Only", "Objection Handling") */
    name: string;
    /** Short description for UI */
    description: string;
    /** What specific skill does this mode train? */
    focusArea: string;
    /** Full instructions for AI prompt */
    promptInstructions: string;
  }>;

  /**
   * AI Coaching Feedback System: Post-session analysis prompt
   * 
   * This prompt is sent to an LLM along with the full conversation transcript
   * to generate structured feedback for the trainee.
   */
  coachingPrompt: {
    /** System prompt that defines the coach's role and expertise */
    systemPrompt: string;
    /** Template for analyzing the conversation (use {{transcript}} placeholder) */
    analysisTemplate: string;
    /** What criteria should the coach evaluate? */
    evaluationCriteria: string[];
    /** Expected output format (JSON schema) */
    outputFormat: {
      strengths: string; // Description of what to include
      weaknesses: string; // Description of what to include
      recommendations: string; // Description of what to include
      score: string; // How to calculate score (0-100)
    };
  };

  /**
   * Branding Configuration: Visual identity and terminology
   */
  branding: {
    /** Primary brand color (hex code) */
    primaryColor: string;
    /** Secondary accent color (hex code) */
    secondaryColor: string;
    /** Background color (hex code) */
    backgroundColor: string;
    /** Logo URL or file path */
    logo?: string;
    /** Platform name (e.g., "FLEXX FIBER Sales Training") */
    platformName: string;
    /** Tagline (e.g., "Master your door-to-door pitch with AI-powered roleplay") */
    tagline: string;
    /** Domain-specific terminology overrides */
    terminology: {
      /** What to call a training session (default: "session") */
      session?: string;
      /** What to call the AI character (default: "AI") */
      aiCharacter?: string;
      /** What to call the trainee (default: "user") */
      trainee?: string;
      /** What to call practice content (default: "script") */
      practiceContent?: string;
      /** What to call the goal (default: "goal") */
      objective?: string;
    };
  };

  /**
   * Voice Integration Configuration: Which voice provider to use
   */
  voiceIntegration: {
    /** Voice provider (e.g., "hume", "elevenlabs", "openai") */
    provider: "hume" | "elevenlabs" | "openai" | "custom";
    /** Provider-specific configuration */
    config: {
      /** Male voice ID/config */
      maleVoice?: string;
      /** Female voice ID/config */
      femaleVoice?: string;
      /** Additional provider-specific settings */
      [key: string]: any;
    };
  };

  /**
   * Optional: Custom Scripts/Content System
   * 
   * Some verticals (like sales) have structured content (scripts).
   * Others (like therapy) may not need this.
   */
  contentSystem?: {
    /** Is the content system enabled? */
    enabled: boolean;
    /** What type of content? (e.g., "scripts", "scenarios", "frameworks") */
    contentType: string;
    /** Content categories */
    categories: Array<{
      id: string;
      name: string;
      description: string;
    }>;
  };

  /**
   * Optional: Additional Features
   */
  features?: {
    /** Enable phone call integration via Twilio? */
    phoneIntegration?: boolean;
    /** Enable session replay? */
    sessionReplay?: boolean;
    /** Enable practice streaks? */
    practiceStreaks?: boolean;
    /** Enable leaderboards? */
    leaderboards?: boolean;
    /** Enable manager/coach dashboard? */
    managerDashboard?: boolean;
  };
}

/**
 * Example: Sales Vertical Config (Simplified)
 */
export const salesVerticalExample: VerticalConfig = {
  metadata: {
    id: "sales",
    name: "Door-to-Door Sales Training",
    description: "AI-powered roleplay training for fiber internet sales reps",
    version: "1.0.0",
    author: "FLEXX FIBER",
  },
  domain: {
    name: "Door-to-door fiber internet sales",
    traineeRole: "Sales rep",
    aiRole: "Homeowner",
    goal: "Close the sale or get an appointment",
    context: "You're selling fiber internet door-to-door. The homeowner is at their front door, interrupted from their day.",
  },
  personas: [
    {
      id: "lamb",
      name: "Lamb",
      emoji: "🐑",
      description: "Friendly, trusting, eager to listen",
      traits: "You are friendly, trusting, and eager to listen. You're open to new ideas and appreciate when someone takes the time to explain things clearly.",
      responseExamples: [
        "Oh, that sounds interesting! Tell me more.",
        "I appreciate you explaining that. What else should I know?",
        "That makes sense. How does the installation work?",
        "I'm glad you stopped by. This is helpful information.",
      ],
      objectionStyle: "Polite and apologetic: 'I'm sorry, but I need to check with my spouse first.' or 'I hope you understand, I just need a bit more time to think about it.'",
    },
    // ... 3 more personas
  ],
  difficultyLevels: [
    {
      id: "rookie",
      name: "Rookie",
      description: "Easy practice - minimal objections",
      parameters: {
        turnsToClose: { min: 5, max: 7 },
        objectionCount: { min: 1, max: 2 },
        pauseLength: { min: 1, max: 2 },
        minimalResponseRate: 20,
      },
      promptModifier: "You're relatively easy to work with. Show interest after 2-3 good answers from rep. Give minimal objections (1-2 max). Ready to close after 5-7 exchanges if rep does well.",
    },
    // ... 4 more levels
  ],
  practiceModes: [
    {
      id: "full_pitch",
      name: "Full Pitch",
      description: "Complete conversation from greeting to close",
      focusArea: "End-to-end sales process",
      promptInstructions: "Engage in a complete door-to-door sales conversation from initial greeting through close.",
    },
    // ... 4-6 more modes
  ],
  coachingPrompt: {
    systemPrompt: "You are an expert door-to-door sales coach with 20+ years of experience training top-performing reps.",
    analysisTemplate: "Analyze this sales conversation between a rep and a homeowner. Provide specific, actionable feedback.\n\nConversation:\n{{transcript}}",
    evaluationCriteria: [
      "Opening approach and first impression",
      "Qualification and discovery questions",
      "Value proposition clarity",
      "Objection handling",
      "Closing technique",
    ],
    outputFormat: {
      strengths: "List 2-3 specific things the rep did well",
      weaknesses: "List 2-3 specific areas for improvement",
      recommendations: "Provide 2-3 actionable next steps",
      score: "Rate 0-100 based on: opening (20pts), discovery (20pts), value prop (20pts), objection handling (20pts), close (20pts)",
    },
  },
  branding: {
    primaryColor: "#00d4ff",
    secondaryColor: "#9333ea",
    backgroundColor: "#0a1628",
    platformName: "FLEXX FIBER Sales Training",
    tagline: "Master your door-to-door pitch with AI-powered roleplay",
    terminology: {
      session: "practice session",
      aiCharacter: "homeowner",
      trainee: "sales rep",
      practiceContent: "script",
      objective: "close",
    },
  },
  voiceIntegration: {
    provider: "hume",
    config: {
      maleVoice: "HUME_MALE_CONFIG_ID",
      femaleVoice: "HUME_FEMALE_CONFIG_ID",
    },
  },
  contentSystem: {
    enabled: true,
    contentType: "scripts",
    categories: [
      { id: "full_pitch", name: "Full Pitch", description: "Complete sales scripts" },
      { id: "objection", name: "Objection Handling", description: "Responses to common objections" },
      { id: "opener", name: "Openers", description: "Door opening scripts" },
    ],
  },
  features: {
    phoneIntegration: true,
    sessionReplay: false,
    practiceStreaks: true,
    leaderboards: true,
    managerDashboard: true,
  },
};
