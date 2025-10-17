import { ApiTester } from "@/components/api-tester"

export default function DebugPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <h1 className="text-3xl font-bold mb-8 text-center">API Debug Panel</h1>
        <ApiTester />
      </div>
    </div>
  )
}