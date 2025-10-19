"use client"

import { useEffect, useState, useMemo } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card } from "@/components/ui/card"
import { Search, Download, FileText, TrendingUp, ArrowLeft, Calendar, Building2, Image as ImageIcon, ChevronDown, ChevronUp } from "lucide-react"
import Link from "next/link"
import { documentsService, chatsService, imagesService, API_CONFIG } from "@/lib/services"
import type { Document, Chat, Image } from "@/lib/types"

interface ChatWithContent {
  chat: Chat
  documents: Document[]
  images: Image[]
}

export function HistoryView() {
  const [loading, setLoading] = useState(false)
  const [chatsWithContent, setChatsWithContent] = useState<ChatWithContent[]>([])
  const [query, setQuery] = useState("")
  const [documentsToShow, setDocumentsToShow] = useState<Record<string, number>>({})
  const [imagesToShow, setImagesToShow] = useState<Record<string, number>>({})

  const defaultUser = API_CONFIG.DEFAULT_USER_ID

  useEffect(() => {
    const load = async () => {
      try {
        setLoading(true)

        // Fetch all chats for the default user
        const chats = await chatsService.getChatsByUser(defaultUser)

        // Try to fetch documents for the default user
        let docs: Document[] = []
        try {
          docs = await documentsService.getDocumentsByUser(defaultUser)
        } catch (docError) {
          console.warn('Error loading documents:', docError)
          // Continue without documents if endpoint fails
        }

        // Try to fetch images for the default user
        let images: Image[] = []
        try {
          images = await imagesService.getImagesByUser(defaultUser)
        } catch (imgError) {
          console.warn('Error loading images:', imgError)
          // Continue without images if endpoint fails
        }

        // Group documents by chat_id
        const docsByChat: Record<string, Document[]> = {}
        docs.forEach((d) => {
          const key = d.chat_id || "unassigned"
          if (!docsByChat[key]) docsByChat[key] = []
          docsByChat[key].push(d)
        })

        // Group images by chat_id and sort by creation date
        const imagesByChat: Record<string, Image[]> = {}
        images.forEach((img) => {
          const key = img.chat_id || "unassigned"
          if (!imagesByChat[key]) imagesByChat[key] = []
          imagesByChat[key].push(img)
        })
        
        // Sort images in each chat by creation date (newest first)
        Object.keys(imagesByChat).forEach(chatId => {
          imagesByChat[chatId].sort((a, b) => {
            const dateA = a.created_at ? new Date(a.created_at).getTime() : 0
            const dateB = b.created_at ? new Date(b.created_at).getTime() : 0
            return dateB - dateA // Newest first
          })
        })

        // Compose chat entries and include documents and images (if any)
        const entries: ChatWithContent[] = chats.map((c) => ({ 
          chat: c, 
          documents: docsByChat[c.chat_id] || [],
          images: imagesByChat[c.chat_id] || []
        }))

        // Sort by created_at descending (newest first)
        entries.sort((a, b) => {
          const ta = a.chat.created_at ? new Date(a.chat.created_at).getTime() : 0
          const tb = b.chat.created_at ? new Date(b.chat.created_at).getTime() : 0
          return tb - ta
        })

        setChatsWithContent(entries)
      } catch (err) {
        console.error("Error loading history:", err)
      } finally {
        setLoading(false)
      }
    }

    load()
  }, [defaultUser])

  const filtered = useMemo(() => {
    if (!query) return chatsWithContent
    const q = query.toLowerCase()
    return chatsWithContent.filter((e: ChatWithContent) => (e.chat.chat_name || "").toLowerCase().includes(q))
  }, [query, chatsWithContent])

  const toggleDocumentsExpansion = (chatId: string, totalDocuments: number) => {
    setDocumentsToShow(prev => {
      const current = prev[chatId] || 4
      const nextCount = current + 4
      return {
        ...prev,
        [chatId]: nextCount >= totalDocuments ? totalDocuments : nextCount
      }
    })
  }

  const collapseDocuments = (chatId: string) => {
    setDocumentsToShow(prev => ({
      ...prev,
      [chatId]: 4
    }))
  }

  const toggleImagesExpansion = (chatId: string, totalImages: number) => {
    setImagesToShow(prev => {
      const current = prev[chatId] || 4
      const nextCount = current + 4
      return {
        ...prev,
        [chatId]: nextCount >= totalImages ? totalImages : nextCount
      }
    })
  }

  const collapseImages = (chatId: string) => {
    setImagesToShow(prev => ({
      ...prev,
      [chatId]: 4
    }))
  }

  const openAllContent = (documents: Document[], images: Image[]) => {
    // Recopilar todas las URLs válidas
    const allUrls: string[] = []
    
    // Agregar URLs de documentos
    documents.forEach((d: Document) => {
      const url = d.pdf_presigned_url || d.pdf_report_link
      if (url && url !== '#') {
        allUrls.push(url)
      }
    })
    
    // Agregar URLs de imágenes
    images.forEach((img: Image) => {
      if (img.image_presigned_url) {
        allUrls.push(img.image_presigned_url)
      }
    })
    
    // Método 1: Intentar abrir todas inmediatamente
    const openImmediately = () => {
      allUrls.forEach(url => window.open(url, '_blank'))
    }
    
    // Método 2: Abrir con delay
    const openWithDelay = () => {
      allUrls.forEach((url, index) => {
        setTimeout(() => {
          window.open(url, '_blank')
        }, index * 300) // 300ms de delay entre cada ventana
      })
    }
    
    // Método 3: Abrir una por una pidiendo confirmación del usuario
    const openOneByOne = async () => {
      for (const url of allUrls) {
        window.open(url, '_blank')
        // Pequeña pausa para que el navegador procese cada apertura
        await new Promise(resolve => setTimeout(resolve, 100))
      }
    }
    
    // Usar método 3 por defecto (más confiable)
    openOneByOne()
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <div className="border-b border-border bg-card">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center gap-4 mb-4">
            <Link href="/">
              <Button variant="ghost" size="icon" className="text-card-foreground">
                <ArrowLeft className="w-5 h-5" />
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-primary" />
              <h1 className="font-semibold text-xl text-card-foreground">Deep Market Analyzer</h1>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-card-foreground">Analysis History</h2>
            <div className="relative w-80">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <Input
                placeholder="Search analysis..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                className="pl-9 bg-background border-border text-foreground placeholder:text-muted-foreground"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Content */}
      <ScrollArea className="h-[calc(100vh-140px)]">
        <div className="max-w-7xl mx-auto px-6 py-8">
          <div className="space-y-4">
            {filtered.length === 0 && !loading ? (
              <div className="text-center text-muted-foreground py-8">No analysis found</div>
            ) : (
              filtered.map(({ chat, documents, images }: ChatWithContent) => (
                <Card key={chat.chat_id} className="p-6 bg-card border-border hover:border-primary/50 transition-colors">
                  <div className="flex items-start justify-between gap-6">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-lg">
                          <Building2 className="w-4 h-4 text-primary" />
                          <span className="font-medium text-sm text-card-foreground">{chat.chat_name || 'Analysis'}</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-2 mb-3">
                        <Calendar className="w-4 h-4 text-muted-foreground" />
                        <span className="text-sm text-muted-foreground">{chat.created_at ? new Date(chat.created_at).toLocaleString() : ''}</span>
                      </div>

                      <div className="space-y-2">
                        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">Generated Documents</h4>
                        <div className="flex flex-wrap gap-2">
                          {documents.length === 0 ? (
                            <div className="text-sm text-muted-foreground">No documents generated for this analysis</div>
                          ) : (
                            <>
                              {documents
                                .slice(0, documentsToShow[chat.chat_id] || 4)
                                .map((doc) => (
                                  <Button
                                    key={doc.document_id}
                                    variant="outline"
                                    size="sm"
                                    className="bg-background hover:bg-accent border-border text-foreground"
                                    onClick={() => window.open(doc.pdf_presigned_url || doc.pdf_report_link || '#', '_blank')}
                                  >
                                    <FileText className="w-4 h-4 mr-2 text-primary" />
                                    {doc.name || `Report ${doc.document_id.slice(-8)}`}
                                    <Download className="w-3 h-3 ml-2 text-muted-foreground" />
                                  </Button>
                                ))
                              }
                              {documents.length > 4 && (
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="text-primary hover:text-primary/80"
                                  onClick={() => {
                                    const currentShowing = documentsToShow[chat.chat_id] || 4
                                    if (currentShowing >= documents.length) {
                                      collapseDocuments(chat.chat_id)
                                    } else {
                                      toggleDocumentsExpansion(chat.chat_id, documents.length)
                                    }
                                  }}
                                >
                                  {(documentsToShow[chat.chat_id] || 4) >= documents.length ? (
                                    <>
                                      <ChevronUp className="w-4 h-4 mr-1" />
                                      Ver menos
                                    </>
                                  ) : (
                                    <>
                                      <ChevronDown className="w-4 h-4 mr-1" />
                                      Ver {Math.min(4, documents.length - (documentsToShow[chat.chat_id] || 4))} más
                                    </>
                                  )}
                                </Button>
                              )}
                            </>
                          )}
                        </div>
                      </div>

                      {/* Generated Images Section */}
                      <div className="space-y-2 mt-4">
                        <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                          Generated Images
                        </h4>
                        {images.length === 0 ? (
                          <div className="text-sm text-muted-foreground">No images generated for this analysis</div>
                        ) : (
                          <>
                            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
                              {images
                                .slice(0, imagesToShow[chat.chat_id] || 4)
                                .map((img: Image, index: number) => (
                                  <div
                                    key={img.image_id}
                                    className="group relative cursor-pointer border rounded-lg overflow-hidden bg-white hover:shadow-md transition-shadow"
                                    onClick={() => window.open(img.image_presigned_url, '_blank')}
                                  >
                                    <img
                                      src={img.image_presigned_url}
                                      alt={img.description}
                                      className="w-full h-24 object-cover group-hover:opacity-90 transition-opacity"
                                      onError={(e) => {
                                        const target = e.target as HTMLImageElement;
                                        target.src = '/placeholder-image.png';
                                      }}
                                    />
                                    <div className="absolute inset-0 bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                      <span className="text-white text-xs font-medium bg-white/20 px-2 py-1 rounded">
                                        Ver imagen
                                      </span>
                                    </div>
                                    <div className="p-2">
                                      <p className="text-xs text-gray-600 truncate">
                                        {img.description || `Image ${index + 1}`}
                                      </p>
                                    </div>
                                  </div>
                                ))
                              }
                            </div>
                            {images.length > 4 && (
                              <div className="mt-3">
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  className="text-primary hover:text-primary/80"
                                  onClick={() => {
                                    const currentShowing = imagesToShow[chat.chat_id] || 4
                                    if (currentShowing >= images.length) {
                                      collapseImages(chat.chat_id)
                                    } else {
                                      toggleImagesExpansion(chat.chat_id, images.length)
                                    }
                                  }}
                                >
                                  {(imagesToShow[chat.chat_id] || 4) >= images.length ? (
                                    <>
                                      <ChevronUp className="w-4 h-4 mr-1" />
                                      Ver menos imágenes
                                    </>
                                  ) : (
                                    <>
                                      <ChevronDown className="w-4 h-4 mr-1" />
                                      Ver {Math.min(4, images.length - (imagesToShow[chat.chat_id] || 4))} imágenes más
                                    </>
                                  )}
                                </Button>
                              </div>
                            )}
                          </>
                        )}
                      </div>
                    </div>

                    <div className="flex flex-col gap-2">
                      <Button 
                        variant="outline" 
                        size="sm" 
                        className="bg-background hover:bg-accent border-border" 
                        disabled={documents.length === 0 && images.length === 0}
                        onClick={() => openAllContent(documents, images)}
                      >
                        <Download className="w-4 h-4 mr-2" />
                        {documents.length + images.length > 0 ? `Abrir Todo (${documents.length + images.length} elementos)` : 'Sin contenido'}
                      </Button>
                      <Link href={`/`}> 
                        <Button variant="outline" size="sm" className="w-full bg-background hover:bg-accent border-border">View Chat</Button>
                      </Link>
                    </div>
                  </div>
                </Card>
              ))
            )}
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
