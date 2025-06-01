"use client"

import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { VickyStatus } from "./vicky-status"
import { VickyCore } from "./vicky-core"
import { VickyPersonality } from "./vicky-personality"
import { VickyHistory } from "./vicky-history"
import { VickyLearning } from "./vicky-learning"
import { VickyExperimental } from "./vicky-experimental"
import { VickyChat } from "./vicky-chat"

export function VickyAITabs() {
  return (
    <Tabs defaultValue="status" className="w-full">
      <TabsList className="grid w-full grid-cols-7 bg-voka-blue-black border-voka-border">
        <TabsTrigger value="status" className="data-[state=active]:bg-voka-magenta data-[state=active]:text-white">
          Status
        </TabsTrigger>
        <TabsTrigger value="core" className="data-[state=active]:bg-voka-magenta data-[state=active]:text-white">
          Core
        </TabsTrigger>
        <TabsTrigger value="chat" className="data-[state=active]:bg-voka-magenta data-[state=active]:text-white">
          Chat
        </TabsTrigger>
        <TabsTrigger value="personality" className="data-[state=active]:bg-voka-magenta data-[state=active]:text-white">
          Personality
        </TabsTrigger>
        <TabsTrigger value="history" className="data-[state=active]:bg-voka-magenta data-[state=active]:text-white">
          History
        </TabsTrigger>
        <TabsTrigger value="learning" className="data-[state=active]:bg-voka-magenta data-[state=active]:text-white">
          Learning
        </TabsTrigger>
        <TabsTrigger
          value="experimental"
          className="data-[state=active]:bg-voka-magenta data-[state=active]:text-white"
        >
          Experimental
        </TabsTrigger>
      </TabsList>

      <TabsContent value="status" className="mt-6">
        <VickyStatus />
      </TabsContent>

      <TabsContent value="core" className="mt-6">
        <VickyCore />
      </TabsContent>

      <TabsContent value="chat" className="mt-6">
        <div className="h-[600px]">
          <VickyChat />
        </div>
      </TabsContent>

      <TabsContent value="personality" className="mt-6">
        <VickyPersonality />
      </TabsContent>

      <TabsContent value="history" className="mt-6">
        <VickyHistory />
      </TabsContent>

      <TabsContent value="learning" className="mt-6">
        <VickyLearning />
      </TabsContent>

      <TabsContent value="experimental" className="mt-6">
        <VickyExperimental />
      </TabsContent>
    </Tabs>
  )
}
