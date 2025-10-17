"use client"

import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Search, Plus, Send, MoreVertical, Edit2, Trash2, Download, TrendingUp, History, Menu, X, AlertCircle, Bot, User } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"
import Link from "next/link"
import { useChats } from "@/hooks/use-chats"

export function ChatInterface() {
  const {
    chats,
    activeChat,
    messages,
    loading,
    sending,
    error,
    createNewChat,
    sendMessage,
    deleteChat,
    switchToChat,
    clearError,
  } = useChats();

  const [searchQuery, setSearchQuery] = useState("");
  const [inputMessage, setInputMessage] = useState("");
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [isCreateChatDialogOpen, setIsCreateChatDialogOpen] = useState(false);
  const [newChatName, setNewChatName] = useState("");
  const [pendingMessage, setPendingMessage] = useState("");

  const handleSendMessage = useCallback(async () => {
    if (!inputMessage.trim() || sending) return;

    // If there's no active chat, save message and open dialog to create a new one
    if (!activeChat) {
      setPendingMessage(inputMessage);
      setNewChatName("");
      setIsCreateChatDialogOpen(true);
      return;
    }

    try {
      const messageToSend = inputMessage;
      setInputMessage(""); // Clear input immediately

      await sendMessage(messageToSend, activeChat);
    } catch (error) {
      console.error("Error sending message:", error);
    }
  }, [inputMessage, sending, activeChat, sendMessage]);

  const handleNewChat = useCallback(() => {
    setNewChatName("");
    setIsCreateChatDialogOpen(true);
  }, []);

  const handleCreateChatConfirm = useCallback(async () => {
    if (!newChatName.trim()) return;
    
    try {
      const chatId = await createNewChat(newChatName);
      setIsCreateChatDialogOpen(false);
      setNewChatName("");
      
      // If there's a pending message, send it to the new chat
      if (pendingMessage.trim()) {
        setInputMessage(""); // Clear input
        await sendMessage(pendingMessage, chatId);
        setPendingMessage("");
      }
    } catch (error) {
      console.error("Error creating new chat:", error);
    }
  }, [createNewChat, newChatName, pendingMessage, sendMessage]);

  const handleDeleteChat = useCallback(async (chatId: string) => {
    try {
      await deleteChat(chatId);
    } catch (error) {
      console.error("Error deleting chat:", error);
    }
  }, [deleteChat]);

  const filteredChats = chats.filter((chat) => 
    chat.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const currentChat = chats.find(chat => chat.id === activeChat);

  return (
    <div className="flex h-screen bg-background overflow-hidden">
      {/* Sidebar */}
      <div
        className={`${
          isSidebarOpen ? "w-80" : "w-0"
        } border-r border-border bg-sidebar flex flex-col transition-all duration-300 overflow-hidden md:relative absolute md:z-0 z-50 h-full`}
      >
        <div className="w-80 flex flex-col h-full">
          {/* Header */}
          <div className="p-4 border-b border-sidebar-border shrink-0">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-primary" />
                <h1 className="font-semibold text-lg text-sidebar-foreground">Deep Market Analyzer</h1>
              </div>
              <Button
                variant="ghost"
                size="icon"
                onClick={() => setIsSidebarOpen(false)}
                className="md:hidden text-sidebar-foreground"
              >
                <X className="w-5 h-5" />
              </Button>
            </div>
            <Dialog open={isCreateChatDialogOpen} onOpenChange={setIsCreateChatDialogOpen}>
              <DialogTrigger asChild>
                <Button 
                  onClick={handleNewChat} 
                  disabled={loading}
                  className="w-full bg-primary hover:bg-primary/90 text-primary-foreground"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  New Analysis
                </Button>
              </DialogTrigger>
              <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                  <DialogTitle>Create New Analysis</DialogTitle>
                  <DialogDescription>
                    Give your analysis session a descriptive name to help identify it later.
                    {pendingMessage && (
                      <span className="block mt-2 text-sm font-medium text-foreground">
                        Your message: &ldquo;{pendingMessage.substring(0, 50)}{pendingMessage.length > 50 ? '...' : ''}&rdquo;
                      </span>
                    )}
                  </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                  <Input
                    placeholder="e.g., Tech Startup Competitive Analysis"
                    value={newChatName}
                    onChange={(e) => setNewChatName(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleCreateChatConfirm()}
                    autoFocus
                  />
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => {
                    setIsCreateChatDialogOpen(false);
                    setPendingMessage("");
                  }}>
                    Cancel
                  </Button>
                  <Button onClick={handleCreateChatConfirm} disabled={!newChatName.trim()}>
                    Create Analysis
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {/* Search */}
          <div className="p-4 border-b border-sidebar-border shrink-0">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search chats..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-9 bg-sidebar-accent border-sidebar-border text-sidebar-foreground placeholder:text-muted-foreground"
              />
            </div>
          </div>

          {/* Navigation */}
          <div className="px-4 py-2 border-b border-sidebar-border shrink-0">
            <Link href="/history">
              <Button variant="ghost" className="w-full justify-start text-sidebar-foreground hover:bg-sidebar-accent">
                <History className="w-4 h-4 mr-2" />
                Analysis History
              </Button>
            </Link>
          </div>

          {/* Error Display */}
          {error && (
            <div className="p-4">
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-sm">
                  {error}
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={clearError}
                    className="ml-2 h-auto p-0 text-xs underline"
                  >
                    Dismiss
                  </Button>
                </AlertDescription>
              </Alert>
            </div>
          )}

          {/* Chat List */}
          <ScrollArea className="flex-1 min-h-0">
            <div className="p-2">
              {loading && chats.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">
                  Loading chats...
                </div>
              ) : filteredChats.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">
                  {searchQuery ? 'No chats found' : 'No chats yet. Create your first analysis!'}
                </div>
              ) : (
                filteredChats.map((chat) => (
                  <div
                    key={chat.id}
                    className={`group p-3 rounded-lg mb-1 cursor-pointer transition-colors ${
                      activeChat === chat.id ? "bg-sidebar-accent" : "hover:bg-sidebar-accent/50"
                    }`}
                    onClick={() => switchToChat(chat.id)}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-medium text-sm text-sidebar-foreground truncate">{chat.name}</h3>
                        <p className="text-xs text-muted-foreground truncate mt-1">{chat.lastMessage}</p>
                        <p className="text-xs text-muted-foreground mt-1">{chat.timestamp}</p>
                      </div>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="opacity-0 group-hover:opacity-100 transition-opacity h-8 w-8"
                          >
                            <MoreVertical className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end" className="bg-popover border-border">
                          <DropdownMenuItem className="text-popover-foreground hover:bg-accent">
                            <Edit2 className="w-4 h-4 mr-2" />
                            Rename
                          </DropdownMenuItem>
                          <DropdownMenuItem 
                            className="text-destructive hover:bg-destructive/10"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteChat(chat.id);
                            }}
                          >
                            <Trash2 className="w-4 h-4 mr-2" />
                            Delete
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  </div>
                ))
              )}
            </div>
          </ScrollArea>
        </div>
      </div>

      {isSidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 md:hidden" onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0 h-full">
        {/* Chat Header */}
        <div className="h-20 border-b border-border px-4 md:px-6 flex items-center justify-between bg-card shrink-0">
          <div className="flex items-center gap-3 min-w-0">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="text-card-foreground shrink-0"
            >
              <Menu className="w-5 h-5" />
            </Button>
            <h2 className="font-semibold text-lg text-card-foreground truncate">
              {currentChat?.name || 'Deep Market Analyzer'}
            </h2>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          <div className="p-4 md:p-6">
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.length === 0 && !loading ? (
                <div className="text-center text-muted-foreground py-8">
                  <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
                  <h3 className="text-lg font-medium mb-2">Welcome to Deep Market Analyzer</h3>
                  <p>Start by telling me about your company to begin the competitive analysis.</p>
                </div>
              ) : (
                messages.map((message) => (
                  <div key={message.id} className={`flex items-start gap-3 w-full ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    {/* Avatar for Assistant (left) */}
                    {message.role === "assistant" && (
                      <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0 mt-1">
                        <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                      </div>
                    )}
                    
                    {/* Message container */}
                    <div className={`relative max-w-[75%] md:max-w-[70%] ${message.role === "user" ? "order-1" : ""}`}>
                      <div
                        className={`rounded-lg p-3 ${
                          message.role === "user"
                            ? "bg-primary text-primary-foreground ml-auto"
                            : "bg-card text-card-foreground border border-border"
                        }`}
                      >
                        <p className="text-sm leading-relaxed whitespace-pre-line">{message.content}</p>
                        
                        {message.hasDownload && (
                          <Button
                            variant="outline"
                            size="sm"
                            className="mt-3 bg-background/50 hover:bg-background border-border"
                          >
                            <Download className="w-4 h-4 mr-2" />
                            Download Research (PDF)
                          </Button>
                        )}
                      </div>
                      
                      {/* Label in the bottom right corner */}
                      <div className={`flex justify-end mt-1 ${message.role === "user" ? "mr-1" : "ml-1"}`}>
                        <span className="text-xs text-muted-foreground">
                          {message.role === "user" ? "You" : "AI Assistant"}
                        </span>
                      </div>
                    </div>

                    {/* Avatar for User (right) */}
                    {message.role === "user" && (
                      <div className="w-8 h-8 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center flex-shrink-0 mt-1 order-2">
                        <User className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                      </div>
                    )}
                  </div>
                ))
              )}
              
              {sending && (
                <div className="flex items-start gap-3 w-full justify-start">
                  <div className="w-8 h-8 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center flex-shrink-0 mt-1">
                    <Bot className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div className="max-w-[75%] md:max-w-[70%]">
                    <div className="bg-card text-card-foreground border border-border rounded-lg p-3">
                      <div className="flex items-center gap-2">
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse"></div>
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 bg-muted-foreground rounded-full animate-pulse" style={{ animationDelay: '0.4s' }}></div>
                        <span className="text-sm text-muted-foreground ml-2">Analyzing your request...</span>
                      </div>
                    </div>
                    <div className="flex justify-end mt-1 ml-1">
                      <span className="text-xs text-muted-foreground">AI Assistant</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-border p-4 bg-card shrink-0">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-2">
              <Input
                placeholder="Type your message..."
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSendMessage()}
                disabled={sending}
                className="flex-1 bg-background border-border text-foreground placeholder:text-muted-foreground"
              />
              <Button
                onClick={handleSendMessage}
                disabled={!inputMessage.trim() || sending}
                className="bg-primary hover:bg-primary/90 text-primary-foreground shrink-0"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>
            <p className="text-xs text-muted-foreground mt-2 text-center">
              The agent will automatically research the necessary context for your analysis
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
