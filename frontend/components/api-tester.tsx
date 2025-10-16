"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { API_CONFIG, chatsService, messagesService, chatAgentService } from "@/lib/services"

export function ApiTester() {
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [chatId, setChatId] = useState("")
  const [chatName, setChatName] = useState("Test Chat")
  const [message, setMessage] = useState("Hello, how are you?")

  const userId = API_CONFIG.DEFAULT_USER_ID

  const handleTest = async (testFunction: () => Promise<any>, description: string) => {
    try {
      setLoading(true)
      setError(null)
      console.log(`Testing: ${description}`)
      const response = await testFunction()
      setResult({ description, response })
      console.log(`Success:`, response)
    } catch (err: any) {
      const errorMessage = err.message || 'Unknown error'
      setError(`${description}: ${errorMessage}`)
      console.error(`Error in ${description}:`, err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>API Endpoint Tester</CardTitle>
          <CardDescription>
            Test your backend endpoints to debug connection issues
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <strong>API Base URL:</strong> {API_CONFIG.BASE_URL}
            </div>
            <div>
              <strong>User ID:</strong> {userId}
            </div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="chats" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="chats">Chats</TabsTrigger>
          <TabsTrigger value="messages">Messages</TabsTrigger>
          <TabsTrigger value="agent">Agent</TabsTrigger>
          <TabsTrigger value="config">Config</TabsTrigger>
        </TabsList>

        <TabsContent value="chats" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Chat Endpoints</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex gap-2">
                <Input
                  placeholder="Chat Name"
                  value={chatName}
                  onChange={(e) => setChatName(e.target.value)}
                />
              </div>
              
              <div className="grid grid-cols-2 gap-2">
                <Button
                  onClick={() => handleTest(
                    () => chatsService.getChatsByUser(userId),
                    "Get Chats by User"
                  )}
                  disabled={loading}
                >
                  Get User Chats
                </Button>
                
                <Button
                  onClick={() => handleTest(
                    () => chatsService.createChat(chatName, userId),
                    "Create New Chat"
                  )}
                  disabled={loading}
                >
                  Create Chat
                </Button>

                {chatId && (
                  <>
                    <Button
                      onClick={() => handleTest(
                        () => chatsService.getChatById(chatId),
                        "Get Chat by ID"
                      )}
                      disabled={loading}
                    >
                      Get Chat by ID
                    </Button>
                    
                    <Button
                      variant="destructive"
                      onClick={() => handleTest(
                        () => chatsService.deleteChat(chatId),
                        "Delete Chat"
                      )}
                      disabled={loading}
                    >
                      Delete Chat
                    </Button>
                  </>
                )}
              </div>
              
              <Input
                placeholder="Chat ID (paste from results)"
                value={chatId}
                onChange={(e) => setChatId(e.target.value)}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="messages" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Message Endpoints</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input
                placeholder="Chat ID"
                value={chatId}
                onChange={(e) => setChatId(e.target.value)}
              />
              
              <Button
                onClick={() => handleTest(
                  () => messagesService.getMessagesByChat(chatId),
                  "Get Messages by Chat"
                )}
                disabled={loading || !chatId}
              >
                Get Messages
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="agent" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Endpoints</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Input
                placeholder="Message to send"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
              />
              <Input
                placeholder="Chat ID (optional - will create new if empty)"
                value={chatId}
                onChange={(e) => setChatId(e.target.value)}
              />
              
              <Button
                onClick={() => handleTest(
                  () => chatAgentService.sendMessage(message, userId, chatId || undefined, chatName),
                  "Send Message to Agent"
                )}
                disabled={loading || !message}
              >
                Send to Agent
              </Button>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="config" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Configuration Test</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                onClick={() => handleTest(
                  async () => {
                    const response = await fetch(`${API_CONFIG.BASE_URL}/health`)
                    if (response.ok) {
                      return await response.json()
                    } else {
                      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
                    }
                  },
                  "Test Health Endpoint"
                )}
                disabled={loading}
              >
                Test Health Check
              </Button>
              
              <Button
                onClick={() => handleTest(
                  async () => {
                    const response = await fetch(`${API_CONFIG.BASE_URL}/docs`)
                    return { status: response.status, statusText: response.statusText }
                  },
                  "Test API Docs"
                )}
                disabled={loading}
              >
                Test API Docs
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {result && (
        <Card>
          <CardHeader>
            <CardTitle>Result: {result.description}</CardTitle>
          </CardHeader>
          <CardContent>
            <pre className="bg-gray-100 p-4 rounded text-sm overflow-auto max-h-96">
              {JSON.stringify(result.response, null, 2)}
            </pre>
          </CardContent>
        </Card>
      )}
      
      {loading && (
        <Card>
          <CardContent className="p-4 text-center">
            <div className="animate-spin w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full mx-auto"></div>
            <p className="mt-2">Testing endpoint...</p>
          </CardContent>
        </Card>
      )}
    </div>
  )
}