"use client"

import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { Card } from "@/components/ui/card"
import { Search, Download, FileText, TrendingUp, ArrowLeft, Calendar, Building2 } from "lucide-react"
import Link from "next/link"

interface AnalysisRecord {
  id: string
  company1: string
  company2: string
  date: string
  summary: string
  documents: {
    id: string
    name: string
    type: string
  }[]
}

export function HistoryView() {
  const analyses: AnalysisRecord[] = [
    {
      id: "1",
      company1: "My Footwear Company",
      company2: "Nike",
      date: "Jan 15, 2025",
      summary:
        "Complete analysis of marketing strategies, brand positioning and presence in Latin American markets",
      documents: [
        { id: "1", name: "General Nike vs My Company Analysis", type: "PDF" },
        { id: "2", name: "Digital Marketing Comparison", type: "PDF" },
        { id: "3", name: "Product Analysis", type: "PDF" },
      ],
    },
    {
      id: "2",
      company1: "Tech Startup",
      company2: "Microsoft",
      date: "Jan 12, 2025",
      summary:
        "In-depth research on cloud computing strategies, technological innovation and business expansion",
      documents: [
        { id: "4", name: "Complete Competitive Assessment", type: "PDF" },
        { id: "5", name: "Innovation Analysis", type: "PDF" },
      ],
    },
    {
      id: "3",
      company1: "Local Coffee",
      company2: "Starbucks",
      date: "Jan 10, 2025",
      summary:
        "Comparison of business models, customer experience and expansion strategies in the coffee shop sector",
      documents: [
        { id: "6", name: "Coffee Shop Market Analysis", type: "PDF" },
        { id: "7", name: "Customer Experience Strategies", type: "PDF" },
        { id: "8", name: "Price and Product Comparison", type: "PDF" },
      ],
    },
    {
      id: "4",
      company1: "E-commerce Fashion",
      company2: "Zara",
      date: "Jan 8, 2025",
      summary: "Analysis of supply chain, fast fashion, digital presence and omnichannel strategies",
      documents: [{ id: "9", name: "Complete Zara Analysis", type: "PDF" }],
    },
  ]

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
            {analyses.map((analysis) => (
              <Card key={analysis.id} className="p-6 bg-card border-border hover:border-primary/50 transition-colors">
                <div className="flex items-start justify-between gap-6">
                  <div className="flex-1">
                    {/* Companies Comparison */}
                    <div className="flex items-center gap-3 mb-3">
                      <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-lg">
                        <Building2 className="w-4 h-4 text-primary" />
                        <span className="font-medium text-sm text-card-foreground">{analysis.company1}</span>
                      </div>
                      <span className="text-muted-foreground font-medium">vs</span>
                      <div className="flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-lg">
                        <Building2 className="w-4 h-4 text-primary" />
                        <span className="font-medium text-sm text-card-foreground">{analysis.company2}</span>
                      </div>
                    </div>

                    {/* Date */}
                    <div className="flex items-center gap-2 mb-3">
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm text-muted-foreground">{analysis.date}</span>
                    </div>

                    {/* Summary */}
                    <p className="text-sm text-muted-foreground leading-relaxed mb-4">{analysis.summary}</p>

                    {/* Documents */}
                    <div className="space-y-2">
                      <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
                        Generated Documents
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.documents.map((doc) => (
                          <Button
                            key={doc.id}
                            variant="outline"
                            size="sm"
                            className="bg-background hover:bg-accent border-border text-foreground"
                          >
                            <FileText className="w-4 h-4 mr-2 text-primary" />
                            {doc.name}
                            <Download className="w-3 h-3 ml-2 text-muted-foreground" />
                          </Button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex flex-col gap-2">
                    <Button variant="outline" size="sm" className="bg-background hover:bg-accent border-border">
                      <Download className="w-4 h-4 mr-2" />
                      Download All
                    </Button>
                    <Link href="/">
                      <Button
                        variant="outline"
                        size="sm"
                        className="w-full bg-background hover:bg-accent border-border"
                      >
                        View Chat
                      </Button>
                    </Link>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </div>
      </ScrollArea>
    </div>
  )
}
