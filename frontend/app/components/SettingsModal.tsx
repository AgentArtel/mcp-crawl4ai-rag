'use client'

import { useState, useEffect } from 'react'
import { X, Settings, Key, MessageSquare, Save, Eye, EyeOff } from 'lucide-react'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
  onSave: (settings: SettingsData) => void
}

export interface SettingsData {
  openaiApiKey: string
  anthropicApiKey: string
  geminiApiKey: string
  systemPrompt: string
  aiProvider: 'openai' | 'anthropic' | 'gemini'
  model: string
  temperature: number
  maxTokens: number
}

const DEFAULT_SYSTEM_PROMPT = `You are an expert academic advisor for Utah Tech University's Bachelor of Individualized Studies (BIS) program. Your role is to help students create personalized Individualized Academic Plans (IAPs) through natural conversation.

Key Responsibilities:
- Guide students through IAP creation and validation
- Help students discover courses and degree programs
- Conduct market research for career viability
- Validate BIS degree requirements (120 credits, 40+ upper-division, 3+ disciplines)
- Create mission statements, program goals, and learning outcomes
- Track general education and concentration area requirements

Communication Style:
- Be encouraging, supportive, and student-focused
- Ask clarifying questions to understand student goals
- Explain complex requirements in simple terms
- Celebrate student progress and achievements
- Provide specific, actionable guidance

Available Tools:
You have access to 28 MCP tools for course search, market research, credit analysis, IAP management, and requirement validation. Use these tools automatically based on conversation context.

Always prioritize the student's academic success and help them create a meaningful, viable degree emphasis.`

export default function SettingsModal({ isOpen, onClose, onSave }: SettingsModalProps) {
  const [settings, setSettings] = useState<SettingsData>({
    openaiApiKey: '',
    anthropicApiKey: '',
    geminiApiKey: '',
    systemPrompt: DEFAULT_SYSTEM_PROMPT,
    aiProvider: 'openai',
    model: 'gpt-4',
    temperature: 0.7,
    maxTokens: 4000
  })
  
  const [showApiKeys, setShowApiKeys] = useState(false)
  const [activeTab, setActiveTab] = useState<'api' | 'prompt' | 'model'>('api')

  useEffect(() => {
    // Load settings from localStorage
    const savedSettings = localStorage.getItem('iap-advisor-settings')
    if (savedSettings) {
      setSettings({ ...settings, ...JSON.parse(savedSettings) })
    }
  }, [])

  const handleSave = () => {
    // Save to localStorage
    localStorage.setItem('iap-advisor-settings', JSON.stringify(settings))
    onSave(settings)
    onClose()
  }

  const handleReset = () => {
    setSettings({
      ...settings,
      systemPrompt: DEFAULT_SYSTEM_PROMPT
    })
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center space-x-2">
            <Settings className="h-5 w-5 text-blue-600" />
            <h2 className="text-xl font-semibold">AI Assistant Settings</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b">
          <button
            onClick={() => setActiveTab('api')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'api'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Key className="h-4 w-4 inline mr-2" />
            API Configuration
          </button>
          <button
            onClick={() => setActiveTab('prompt')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'prompt'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <MessageSquare className="h-4 w-4 inline mr-2" />
            System Prompt
          </button>
          <button
            onClick={() => setActiveTab('model')}
            className={`px-6 py-3 font-medium ${
              activeTab === 'model'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Model Settings
          </button>
        </div>

        {/* Content */}
        <div className="p-6 overflow-y-auto max-h-[60vh]">
          {activeTab === 'api' && (
            <div className="space-y-6">
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  <strong>Important:</strong> API keys are stored locally in your browser and never sent to our servers. 
                  You need at least one API key to enable AI responses.
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  AI Provider
                </label>
                <select
                  value={settings.aiProvider}
                  onChange={(e) => setSettings({
                    ...settings,
                    aiProvider: e.target.value as 'openai' | 'anthropic',
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="openai">OpenAI (GPT-4, GPT-3.5)</option>
                  <option value="anthropic">Anthropic (Claude)</option>
                  <option value="gemini">Google (Gemini)</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  OpenAI API Key
                </label>
                <div className="relative">
                  <input
                    type={showApiKeys ? 'text' : 'password'}
                    value={settings.openaiApiKey}
                    onChange={(e) => setSettings({ ...settings, openaiApiKey: e.target.value })}
                    placeholder="sk-..."
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKeys(!showApiKeys)}
                    className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                  >
                    {showApiKeys ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Get your API key from <a href="https://platform.openai.com/api-keys" target="_blank" className="text-blue-600 hover:underline">OpenAI Platform</a>
                </p>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Anthropic API Key
                </label>
                <div className="relative">
                  <input
                    type={showApiKeys ? "text" : "password"}
                    value={settings.anthropicApiKey}
                    onChange={(e) => setSettings({ ...settings, anthropicApiKey: e.target.value })}
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="sk-ant-..."
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKeys(!showApiKeys)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showApiKeys ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Google Gemini API Key
                </label>
                <div className="relative">
                  <input
                    type={showApiKeys ? "text" : "password"}
                    value={settings.geminiApiKey}
                    onChange={(e) => setSettings({ ...settings, geminiApiKey: e.target.value })}
                    className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="AIza..."
                  />
                  <button
                    type="button"
                    onClick={() => setShowApiKeys(!showApiKeys)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showApiKeys ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                Get your API key from <a href="https://console.cloud.google.com/apis/credentials" target="_blank" className="text-blue-600 hover:underline">Google Cloud Console</a>
              </p>
            </div>
          )}

          {activeTab === 'prompt' && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <label className="block text-sm font-medium text-gray-700">
                  System Prompt
                </label>
                <button
                  onClick={handleReset}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Reset to Default
                </button>
              </div>
              <textarea
                value={settings.systemPrompt}
                onChange={(e) => setSettings({ ...settings, systemPrompt: e.target.value })}
                rows={20}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                placeholder="Enter your system prompt..."
              />
              <p className="text-xs text-gray-500">
                This prompt defines how the AI assistant behaves and responds to students. 
                The default prompt is optimized for Utah Tech IAP advising.
              </p>
            </div>
          )}

          {activeTab === 'model' && (
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Model
                </label>
                <select
                  value={settings.model}
                  onChange={(e) => setSettings({ ...settings, model: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {settings.aiProvider === 'openai' ? (
                    <>
                      <option value="gpt-4">GPT-4 (Recommended)</option>
                      <option value="gpt-4-turbo">GPT-4 Turbo</option>
                      <option value="gpt-3.5-turbo">GPT-3.5 Turbo (Faster, cheaper)</option>
                    </>
                  ) : (
                    <>
                      <option value="claude-3-sonnet-20240229">Claude 3 Sonnet (Recommended)</option>
                      <option value="claude-3-haiku-20240307">Claude 3 Haiku (Faster)</option>
                      <option value="claude-3-opus-20240229">Claude 3 Opus (Most capable)</option>
                    </>
                  )}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Temperature: {settings.temperature}
                </label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={settings.temperature}
                  onChange={(e) => setSettings({ ...settings, temperature: parseFloat(e.target.value) })}
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>More focused</span>
                  <span>More creative</span>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Max Tokens
                </label>
                <input
                  type="number"
                  min="100"
                  max="4000"
                  value={settings.maxTokens}
                  onChange={(e) => setSettings({ ...settings, maxTokens: parseInt(e.target.value) })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Maximum length of AI responses (100-4000 tokens)
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-2"
          >
            <Save className="h-4 w-4" />
            <span>Save Settings</span>
          </button>
        </div>
      </div>
    </div>
  )
}
