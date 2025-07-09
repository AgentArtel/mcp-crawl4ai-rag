'use client'

import { useState, useEffect } from 'react'
import { X, Settings, Key, Brain, Palette, Save } from 'lucide-react'

interface SettingsModalProps {
  isOpen: boolean
  onClose: () => void
  currentSettings: {
    aiProvider: 'openai' | 'anthropic'
    model: string
    temperature: number
    maxTokens: number
    systemPrompt: string
    openaiApiKey: string
    anthropicApiKey: string
  }
  onSave: (settings: any) => void
}

export default function SettingsModal({ isOpen, onClose, currentSettings, onSave }: SettingsModalProps) {
  const [settings, setSettings] = useState(currentSettings)
  const [activeTab, setActiveTab] = useState('ai')
  const [showApiKeys, setShowApiKeys] = useState(false)

  useEffect(() => {
    setSettings(currentSettings)
  }, [currentSettings])

  if (!isOpen) return null

  const handleSave = () => {
    onSave(settings)
    onClose()
  }

  const tabs = [
    { id: 'ai', label: 'AI Settings', icon: Brain },
    { id: 'keys', label: 'API Keys', icon: Key },
    { id: 'appearance', label: 'Appearance', icon: Palette }
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-600" />
            <h2 className="text-xl font-semibold">Settings</h2>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex">
          {/* Sidebar */}
          <div className="w-48 bg-gray-50 p-4">
            <nav className="space-y-2">
              {tabs.map((tab) => {
                const Icon = tab.icon
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
                      activeTab === tab.id
                        ? 'bg-blue-100 text-blue-700'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                )
              })}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1 p-6 overflow-y-auto max-h-[60vh]">
            {activeTab === 'ai' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">AI Provider Settings</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">AI Provider</label>
                      <select
                        value={settings.aiProvider}
                        onChange={(e) => setSettings({...settings, aiProvider: e.target.value as 'openai' | 'anthropic'})}
                        className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="openai">OpenAI (GPT-4)</option>
                        <option value="anthropic">Anthropic (Claude)</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Model</label>
                      <select
                        value={settings.model}
                        onChange={(e) => setSettings({...settings, model: e.target.value})}
                        className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        {settings.aiProvider === 'openai' ? (
                          <>
                            <option value="gpt-4">GPT-4</option>
                            <option value="gpt-4-turbo">GPT-4 Turbo</option>
                            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                          </>
                        ) : (
                          <>
                            <option value="claude-3-sonnet-20240229">Claude 3 Sonnet</option>
                            <option value="claude-3-haiku-20240307">Claude 3 Haiku</option>
                            <option value="claude-3-opus-20240229">Claude 3 Opus</option>
                          </>
                        )}
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Temperature: {settings.temperature}
                      </label>
                      <input
                        type="range"
                        min="0"
                        max="2"
                        step="0.1"
                        value={settings.temperature}
                        onChange={(e) => setSettings({...settings, temperature: parseFloat(e.target.value)})}
                        className="w-full"
                      />
                      <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>Focused</span>
                        <span>Balanced</span>
                        <span>Creative</span>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Max Tokens: {settings.maxTokens}
                      </label>
                      <input
                        type="range"
                        min="100"
                        max="4000"
                        step="100"
                        value={settings.maxTokens}
                        onChange={(e) => setSettings({...settings, maxTokens: parseInt(e.target.value)})}
                        className="w-full"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">System Prompt</label>
                      <textarea
                        value={settings.systemPrompt}
                        onChange={(e) => setSettings({...settings, systemPrompt: e.target.value})}
                        rows={4}
                        className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="Customize the AI's behavior and personality..."
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'keys' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">API Keys</h3>
                  <p className="text-sm text-gray-600 mb-4">
                    Your API keys are stored securely in your browser and never sent to our servers.
                  </p>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">OpenAI API Key</label>
                      <div className="relative">
                        <input
                          type={showApiKeys ? "text" : "password"}
                          value={settings.openaiApiKey}
                          onChange={(e) => setSettings({...settings, openaiApiKey: e.target.value})}
                          className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent pr-20"
                          placeholder="sk-..."
                        />
                        <button
                          type="button"
                          onClick={() => setShowApiKeys(!showApiKeys)}
                          className="absolute right-2 top-2 text-sm text-blue-600 hover:text-blue-800"
                        >
                          {showApiKeys ? 'Hide' : 'Show'}
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Anthropic API Key</label>
                      <input
                        type={showApiKeys ? "text" : "password"}
                        value={settings.anthropicApiKey}
                        onChange={(e) => setSettings({...settings, anthropicApiKey: e.target.value})}
                        className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="sk-ant-..."
                      />
                    </div>

                    <div className="bg-blue-50 p-4 rounded-lg">
                      <h4 className="font-medium text-blue-900 mb-2">How to get API keys:</h4>
                      <ul className="text-sm text-blue-800 space-y-1">
                        <li>• OpenAI: Visit <a href="https://platform.openai.com/api-keys" target="_blank" className="underline">platform.openai.com/api-keys</a></li>
                        <li>• Anthropic: Visit <a href="https://console.anthropic.com/" target="_blank" className="underline">console.anthropic.com</a></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'appearance' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium mb-4">Appearance</h3>
                  
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium mb-2">Theme</label>
                      <div className="grid grid-cols-2 gap-3">
                        <button className="p-3 border rounded-lg text-left hover:bg-gray-50 border-blue-500 bg-blue-50">
                          <div className="font-medium">Light</div>
                          <div className="text-sm text-gray-600">Default theme</div>
                        </button>
                        <button className="p-3 border rounded-lg text-left hover:bg-gray-50">
                          <div className="font-medium">Dark</div>
                          <div className="text-sm text-gray-600">Coming soon</div>
                        </button>
                      </div>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Chat Density</label>
                      <select className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        <option>Comfortable</option>
                        <option>Compact</option>
                        <option>Spacious</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium mb-2">Font Size</label>
                      <select className="w-full p-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                        <option>Small</option>
                        <option>Medium</option>
                        <option>Large</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:text-gray-800 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Save className="w-4 h-4" />
            Save Settings
          </button>
        </div>
      </div>
    </div>
  )
}
