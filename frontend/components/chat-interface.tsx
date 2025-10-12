"use client"

import { useState, useCallback, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Search, Plus, Send, MoreVertical, Edit2, Trash2, Download, TrendingUp, History, Menu, X } from "lucide-react"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import Link from "next/link"

interface Message {
  id: string
  role: "user" | "assistant"
  content: string
  hasDownload?: boolean
}

interface Chat {
  id: string
  name: string
  lastMessage: string
  timestamp: string
}

export function ChatInterface() {
  const idCounter = useRef(1000)
  
  const generateId = useCallback(() => {
    idCounter.current += 1
    return idCounter.current.toString()
  }, [])

  const [chats, setChats] = useState<Chat[]>([
    {
      id: "1",
      name: "Nike vs Adidas Analysis",
      lastMessage: "Marketing strategy comparison...",
      timestamp: "2 hours ago",
    },
    {
      id: "2",
      name: "Coca-Cola Competition",
      lastMessage: "Market research completed",
      timestamp: "Yesterday",
    },
    {
      id: "3",
      name: "Technology Sector",
      lastMessage: "Trend analysis...",
      timestamp: "3 days ago",
    },
  ])

  const [activeChat, setActiveChat] = useState("1")
  const [searchQuery, setSearchQuery] = useState("")
  const [inputMessage, setInputMessage] = useState("")
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your competitive analysis agent. Tell me about your company to start the research.",
    },
    {
      id: "2",
      role: "user",
      content:
        "I want to analyze my sports footwear company. We focus on running and have presence in Latin America.",
    },
    {
      id: "3",
      role: "assistant",
      content:
        "Perfect. I've researched the sports footwear market context in Latin America. Found data on consumption trends, fitness sector growth, and main competitors. Which specific competitor would you like to compare yourself with?",
    },
    {
      id: "4",
      role: "user",
      content: "I would like to compare myself with Nike",
    },
    {
      id: "5",
      role: "assistant",
      content:
        "Excellent choice. I've completed an in-depth analysis of Nike including:\n\n• Marketing strategies and positioning\n• Presence in Latin American markets\n• Product innovation\n• Distribution channels\n• Price analysis\n\nWould you like a general overview or prefer to focus on a specific area like marketing, products, or distribution?",
      hasDownload: true,
    },
  ])

  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const handleSendMessage = useCallback(() => {
    if (!inputMessage.trim()) return

    const newMessage: Message = {
      id: generateId(),
      role: "user",
      content: inputMessage,
    }

    setMessages([...messages, newMessage])
    setInputMessage("")

    // Simulate assistant response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          id: generateId(),
          role: "assistant",
          content: "Processing your request...",
        },
      ])
    }, 1000)
  }, [inputMessage, messages, generateId])

  const handleNewChat = useCallback(() => {
    const newChat: Chat = {
      id: generateId(),
      name: "New analysis",
      lastMessage: "Chat started",
      timestamp: "Now",
    }
    setChats([newChat, ...chats])
    setActiveChat(newChat.id)
    setMessages([
      {
        id: "1",
        role: "assistant",
        content:
          "Hello! I'm your competitive analysis agent. Tell me about your company to start the research.",
      },
    ])
  }, [chats, generateId])

  const filteredChats = chats.filter((chat) => chat.name.toLowerCase().includes(searchQuery.toLowerCase()))

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
            <Button onClick={handleNewChat} className="w-full bg-primary hover:bg-primary/90 text-primary-foreground">
              <Plus className="w-4 h-4 mr-2" />
              New Analysis
            </Button>
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

          {/* Chat List */}
          <ScrollArea className="flex-1 min-h-0">
            <div className="p-2">
              {filteredChats.map((chat) => (
                <div
                  key={chat.id}
                  className={`group p-3 rounded-lg mb-1 cursor-pointer transition-colors ${
                    activeChat === chat.id ? "bg-sidebar-accent" : "hover:bg-sidebar-accent/50"
                  }`}
                  onClick={() => setActiveChat(chat.id)}
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
                        <DropdownMenuItem className="text-destructive hover:bg-destructive/10">
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </div>
                </div>
              ))}
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
              {chats.find((c) => c.id === activeChat)?.name}
            </h2>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 min-h-0 overflow-y-auto">
          <div className="p-4 md:p-6">
            <div className="max-w-3xl mx-auto space-y-6">
              {messages.map((message) => (
                <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                  <div
                    className={`max-w-[85%] md:max-w-[80%] rounded-lg p-4 ${
                      message.role === "user"
                        ? "bg-primary text-primary-foreground"
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
                </div>
              ))}
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
                onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                className="flex-1 bg-background border-border text-foreground placeholder:text-muted-foreground"
              />
              <Button
                onClick={handleSendMessage}
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
