import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Send, Loader2, Maximize2, Rocket } from "lucide-react";
import { toast } from "sonner";
import { ChartDBViewer, ChartDBViewerRef } from "@/components/ChartDBViewer";
import { TypewriterText } from "@/components/TypewriterText";
import { SchemaSummaryBox } from "@/components/SchemaSummaryBox";
import SailboatIcon from "@/components/SailboatIcon";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";
import { Label } from "@/components/ui/label";

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  isStreaming?: boolean; // Track if message is currently streaming
}

const Chat = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [conversationDone, setConversationDone] = useState(false);
  const [initializing, setInitializing] = useState(true);
  const [leftWidth, setLeftWidth] = useState(30); // Start at 30%
  const [isDragging, setIsDragging] = useState(false);
  const [generatedSchema, setGeneratedSchema] = useState<any>(null);
  const [showSchemaModal, setShowSchemaModal] = useState(false);
  const [showDeployDialog, setShowDeployDialog] = useState(false);
  const [isDeploying, setIsDeploying] = useState(false);
  const [databaseName, setDatabaseName] = useState("");
  const [deploymentType, setDeploymentType] = useState<'dynamodb' | 'supabase'>('dynamodb');
  const [selectedDeployment, setSelectedDeployment] = useState<'nosql' | 'postgresql' | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chartDBViewerRef = useRef<ChartDBViewerRef>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  // Track which messages have finished streaming
  const [streamedMessages, setStreamedMessages] = useState<Set<number>>(new Set());

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamedMessages]);

  // Auto-scroll during streaming with a slight delay for smooth animation
  useEffect(() => {
    const hasStreaming = messages.some((msg, idx) => msg.isStreaming && !streamedMessages.has(idx));
    if (hasStreaming) {
      const scrollInterval = setInterval(() => {
        scrollToBottom();
      }, 100);
      return () => clearInterval(scrollInterval);
    }
  }, [messages, streamedMessages]);

  // Handle mouse move for resizing
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isDragging) return;
      
      const container = e.currentTarget as HTMLElement;
      const containerWidth = window.innerWidth;
      const newLeftWidth = (e.clientX / containerWidth) * 100;
      
      // Constrain between 20% and 80%
      const constrainedWidth = Math.max(20, Math.min(80, newLeftWidth));
      setLeftWidth(constrainedWidth);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
    };

    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = 'col-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isDragging]);

  // Auto-start the conversation when component mounts
  useEffect(() => {
    const startConversation = async () => {
      if (sessionId) return; // Already started
      
      console.log('Starting conversation...'); // Debug log
      setIsLoading(true);
      setInitializing(true);
      try {
        console.log('Fetching from:', `${API_BASE_URL}/api/projects/new_project/start`); // Debug log
        const response = await fetch(`${API_BASE_URL}/api/projects/new_project/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ 
            name: "New Database Project",
            description: "I'd like to create a new database" 
          })
        });

        console.log('Response status:', response.status); // Debug log
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log('Start conversation result:', result); // Debug log
        setSessionId(result.session_id);
        setMessages([{ role: 'assistant', content: result.prompt, isStreaming: true }]);
        setInitializing(false);
      } catch (error) {
        console.error('Error starting conversation:', error); // Debug log
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        toast.error(`Error starting conversation: ${errorMessage}`);
        setMessages([{ role: 'assistant', content: 'Sorry, there was an error starting the conversation. Please refresh the page.' }]);
        setInitializing(false);
      } finally {
        setIsLoading(false);
        console.log('Start conversation complete'); // Debug log
      }
    };

    startConversation();
  }, [sessionId]);

  const handleSend = async () => {
    if (!input.trim() || isLoading || !sessionId) return;

    const userMessage = input.trim();
    setInput("");
    setMessages(prev => [...prev, { role: 'user', content: userMessage }]);
    setIsLoading(true);

    try {
      // Continue conversation
      const response = await fetch(`${API_BASE_URL}/api/projects/new_project/next`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: sessionId,
          answer: userMessage
        })
      });

      if (!response.ok) {
        // Try to get detailed error message from response
        let errorDetail = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorData.message || errorDetail;
        } catch {
          // If JSON parsing fails, use status text
          errorDetail = response.statusText || errorDetail;
        }
        
        // Show detailed error to user
        console.error('API error:', errorDetail);
        toast.error(`Error: ${errorDetail}`);
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: `Sorry, there was an error: ${errorDetail}. Please try again or check your API configuration.` 
        }]);
        return;
      }

      const result = await response.json();
      console.log('Chat result:', result); // Debug logging
      setMessages(prev => [...prev, { role: 'assistant', content: result.prompt, isStreaming: true }]);
      
      if (result.done) {
        console.log('Conversation marked as done'); // Debug logging
        setConversationDone(true);
        toast.success("Conversation complete! You can finish to generate the schema.");
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Chat error:', error); // Log full error for debugging
      toast.error(`Error: ${errorMessage}`);
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: `Sorry, there was an error: ${errorMessage}. Please check your connection and try again.` 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFinish = async () => {
    if (!sessionId) return;

    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/projects/new_project/finish`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      toast.success("Schema generated successfully!");
      console.log("Generated spec:", result.spec);
      
      // Store the generated schema
      setGeneratedSchema(result.spec);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      toast.error(`Error: ${errorMessage}`);
    } finally {
      setIsLoading(false);
    }
  };

  // Auto-load visualization when schema changes
  useEffect(() => {
    if (generatedSchema && chartDBViewerRef.current) {
      console.log("Loading visualization for schema...");
      chartDBViewerRef.current.loadSchema(generatedSchema);
    }
  }, [generatedSchema]);

  const handleDeploy = async () => {
    if (!generatedSchema || !databaseName.trim()) {
      toast.error("Please enter a database name");
      return;
    }

    setIsDeploying(true);
    try {
      let endpoint = '';
      let dbType = '';

      if (deploymentType === 'dynamodb') {
        // Check if DynamoDB tables are available
        if (!generatedSchema.dynamodb_tables || generatedSchema.dynamodb_tables.length === 0) {
          toast.error("DynamoDB schema not generated yet. Please wait for the schema to be generated.");
          setShowDeployDialog(false);
          setIsDeploying(false);
          return;
        }
        endpoint = `${API_BASE_URL}/api/projects/deploy`;
        dbType = 'dynamodb';
      } else {
        // Check if PostgreSQL SQL is available
        if (!generatedSchema.postgres_sql || !generatedSchema.postgres_sql.trim()) {
          toast.error("PostgreSQL schema not generated yet. Please wait for the schema to be generated.");
          setShowDeployDialog(false);
          setIsDeploying(false);
          return;
        }
        endpoint = `${API_BASE_URL}/api/projects/deploy-supabase`;
        dbType = 'supabase';
      }

      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          project_id: sessionId || "default",
          database_type: dbType,
          database_name: databaseName,
          spec: generatedSchema
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      toast.success(`Deployment successful! ${result.message}`);
      console.log("Deployment result:", result);
      
      setShowDeployDialog(false);
      setDatabaseName("");
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      toast.error(`Deployment failed: ${errorMessage}`);
    } finally {
      setIsDeploying(false);
    }
  };

  return (
    <div className="h-screen bg-[hsl(var(--background))] flex overflow-hidden">
      {/* Left Side - Chat */}
      <div 
        className="border-r border-border/40 flex flex-col overflow-hidden bg-[hsl(var(--background))]"
        style={{ width: `${leftWidth}%` }}
      >
        {/* Chat Header - IDE-like */}
        <div className="px-5 py-4 border-b border-border/40 bg-[hsl(var(--card))] flex items-center gap-3">
          <SailboatIcon className="w-6 h-6 text-[hsl(var(--primary))]" />
          <div>
            <h2 className="text-lg font-semibold text-foreground tracking-tight">
              ShipDB
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5 font-normal">
              AI Database Designer
            </p>
          </div>
        </div>

        {/* Chat Messages Area - IDE-like */}
        <div className="flex-1 p-5 overflow-y-auto space-y-3 bg-[hsl(var(--background))]">
          {messages.length === 0 && initializing && (
            <div className="text-center text-muted-foreground mt-8">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p className="text-lg">Starting conversation...</p>
            </div>
          )}
          {messages.map((msg, idx) => {
            const isStreaming = msg.isStreaming && !streamedMessages.has(idx);
            return (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-md px-4 py-2.5 ${
                    msg.role === 'user'
                      ? 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] border-2 border-black/20'
                      : 'bg-[hsl(var(--card))] border border-border/40 text-foreground'
                  }`}
                >
                  {msg.role === 'assistant' && isStreaming ? (
                    <p className="text-sm whitespace-pre-wrap leading-relaxed font-normal">
                      <TypewriterText
                        text={msg.content}
                        speed={15}
                        messageKey={idx}
                        onComplete={() => {
                          setStreamedMessages(prev => new Set([...prev, idx]));
                        }}
                      />
                    </p>
                  ) : (
                    <p className="text-sm whitespace-pre-wrap leading-relaxed font-normal">{msg.content}</p>
                  )}
                  
                  {/* Show schema summary box for assistant messages that contain schema info */}
                  {msg.role === 'assistant' && !isStreaming && (
                    <SchemaSummaryBox content={msg.content} />
                  )}
                </div>
              </div>
            );
          })}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-[hsl(var(--card))] border border-border/40 rounded-md px-4 py-3">
                <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
              </div>
            </div>
          )}
          
          
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input - IDE-like */}
        <div className="p-4 border-t border-border/40 space-y-3 bg-[hsl(var(--card))]">
          {conversationDone && (
            <Button
              onClick={handleFinish}
              disabled={isLoading}
              className="w-full bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:bg-[hsl(var(--primary))]/90 h-9 text-sm font-medium rounded-md"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Generating Schema...
                </>
              ) : (
                'Finish & Generate Schema'
              )}
            </Button>
          )}
          
          <div className="flex gap-2">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !isLoading && !initializing && handleSend()}
              placeholder={initializing ? "Starting conversation..." : "Type your response..."}
              className="flex-1 bg-[hsl(var(--background))] border-border/40 text-sm rounded-md h-9 font-normal focus-visible:ring-2 focus-visible:ring-[hsl(var(--ring))]"
              disabled={isLoading || initializing}
            />
            <Button
              onClick={handleSend}
              disabled={isLoading || initializing || !input.trim()}
              className="bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:bg-[hsl(var(--primary))]/90 h-9 w-9 p-0 rounded-md"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
        </div>
      </div>

      {/* Draggable Divider - IDE-like */}
      <div
        className="w-1 bg-border/30 hover:bg-border/60 cursor-col-resize transition-colors relative group"
        onMouseDown={() => setIsDragging(true)}
      >
        <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-4 flex items-center justify-center">
          <div className="w-0.5 h-12 bg-border/40 rounded-full group-hover:bg-[hsl(var(--primary))] transition-colors" />
        </div>
      </div>

      {/* Right Side - ChartDB Visualization - IDE-like */}
      <div 
        className="flex flex-col overflow-hidden flex-1 bg-[hsl(var(--background))]"
        style={{ width: `${100 - leftWidth}%`, minWidth: 0 }}
      >
        {generatedSchema ? (
          <div className="flex-1 flex flex-col overflow-hidden">
            {/* Schema Info - IDE-like toolbar */}
            <div className="flex items-center gap-2 flex-shrink-0 px-4 py-3 border-b border-border/40 bg-[hsl(var(--card))]">
              <Button
                variant="outline"
                size="sm"
                className="flex items-center gap-2 h-8 text-xs bg-[hsl(var(--background))] border-border/40 hover:bg-[hsl(var(--background))]/80"
                onClick={() => setShowSchemaModal(true)}
              >
                <Maximize2 className="h-3.5 w-3.5" />
                <span className="text-xs font-medium">Schema</span>
                <span className="text-xs text-muted-foreground">({generatedSchema.entities?.length || 0})</span>
              </Button>
              
              {/* Deploy Button - IDE-like */}
              {(generatedSchema.dynamodb_tables?.length > 0 || generatedSchema.postgres_sql) && (
                <Button
                  onClick={() => setShowDeployDialog(true)}
                  className="bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] hover:bg-[hsl(var(--primary))]/90 h-8 text-xs font-medium"
                  size="sm"
                >
                  <Rocket className="h-3.5 w-3.5 mr-1.5" />
                  <span className="text-xs">Deploy</span>
                </Button>
              )}
            </div>

            {/* ChartDB Visualization - IDE-like */}
            <div className="flex-1 overflow-hidden relative bg-[hsl(var(--background))]" style={{ minWidth: 0 }}>
              <ChartDBViewer
                ref={chartDBViewerRef}
                projectId={sessionId || "default"}
                deploymentType="supabase"
                onSchemaUpdate={(updatedSchema) => {
                  console.log("Schema updated:", updatedSchema);
                  // Update the generatedSchema state to reflect the changes
                  setGeneratedSchema(updatedSchema);
                  toast.success("Schema updated successfully! Check 'Generated Schema' to see changes.");
                }}
              />
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full bg-[hsl(var(--background))]">
            <div className="text-center text-muted-foreground">
              <p className="text-sm font-medium">Complete the conversation to generate your database schema</p>
              <p className="text-xs mt-2 text-muted-foreground/70">The visualization will appear automatically here</p>
            </div>
          </div>
        )}
      </div>

      {/* Schema Modal - IDE-like */}
      <Dialog open={showSchemaModal} onOpenChange={setShowSchemaModal}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col bg-[hsl(var(--background))] border-border/40">
          <DialogHeader className="pb-3 border-b border-border/40">
            <DialogTitle className="text-base font-semibold">Database Schema - {generatedSchema?.app_type || 'Database'}</DialogTitle>
          </DialogHeader>
          {generatedSchema && (
            <Tabs defaultValue="entities" className="flex-1 overflow-hidden flex flex-col">
              <TabsList>
                <TabsTrigger value="entities">Entities</TabsTrigger>
                <TabsTrigger value="postgres">PostgreSQL</TabsTrigger>
                <TabsTrigger value="json">JSON Schema</TabsTrigger>
                <TabsTrigger value="dynamodb">DynamoDB</TabsTrigger>
              </TabsList>
              
              <TabsContent value="entities" className="flex-1 overflow-y-auto mt-4">
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">App Type</p>
                      <p className="text-lg">{generatedSchema.app_type || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-muted-foreground">Database Type</p>
                      <p className="text-lg">{generatedSchema.db_type || 'N/A'}</p>
                    </div>
                  </div>
                  
                  {generatedSchema.entities && generatedSchema.entities.length > 0 && (
                    <div>
                      <p className="text-sm font-medium text-muted-foreground mb-3">Entities ({generatedSchema.entities.length})</p>
                      <div className="space-y-3">
                        {generatedSchema.entities.map((entity: any, idx: number) => (
                          <div key={idx} className="bg-card border border-border/50 p-4 rounded-lg">
                            <p className="font-semibold text-lg mb-3">{entity.name}</p>
                            {entity.fields && (
                              <div className="space-y-2">
                                {entity.fields.map((field: any, fIdx: number) => (
                                  <div key={fIdx} className="flex items-center gap-2 flex-wrap">
                                    <span className="font-medium">{field.name}</span>
                                    <span className="text-xs bg-muted px-2 py-1 rounded">{field.type}</span>
                                    {field.primary_key && <span className="text-xs bg-blue-500/20 text-blue-500 px-2 py-1 rounded">PK</span>}
                                    {field.foreign_key && <span className="text-xs bg-green-500/20 text-green-500 px-2 py-1 rounded">FK → {field.foreign_key.table}</span>}
                                    {field.unique && <span className="text-xs bg-purple-500/20 text-purple-500 px-2 py-1 rounded">UNIQUE</span>}
                                    {field.required && <span className="text-xs bg-orange-500/20 text-orange-500 px-2 py-1 rounded">REQUIRED</span>}
                                  </div>
                                ))}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </TabsContent>

              <TabsContent value="postgres" className="flex-1 overflow-y-auto mt-4">
                {generatedSchema.postgres_sql ? (
                  <pre className="bg-[hsl(var(--card))] border border-border/40 p-4 rounded-md overflow-x-auto text-xs font-mono text-foreground">
                    {generatedSchema.postgres_sql}
                  </pre>
                ) : (
                  <p className="text-muted-foreground text-sm">PostgreSQL schema not yet generated.</p>
                )}
              </TabsContent>

              <TabsContent value="json" className="flex-1 overflow-y-auto mt-4">
                {generatedSchema.json_schema ? (
                  <pre className="bg-[hsl(var(--card))] border border-border/40 p-4 rounded-md overflow-x-auto text-xs font-mono text-foreground">
                    {JSON.stringify(generatedSchema.json_schema, null, 2)}
                  </pre>
                ) : (
                  <p className="text-muted-foreground text-sm">JSON schema not yet generated.</p>
                )}
              </TabsContent>

              <TabsContent value="dynamodb" className="flex-1 overflow-y-auto mt-4">
                {generatedSchema.dynamodb_tables ? (
                  <pre className="bg-[hsl(var(--card))] border border-border/40 p-4 rounded-md overflow-x-auto text-xs font-mono text-foreground">
                    {JSON.stringify(generatedSchema.dynamodb_tables, null, 2)}
                  </pre>
                ) : (
                  <p className="text-muted-foreground text-sm">DynamoDB schema not yet generated.</p>
                )}
              </TabsContent>
            </Tabs>
          )}
        </DialogContent>
      </Dialog>

      {/* Deploy Dialog */}
      <AlertDialog open={showDeployDialog} onOpenChange={setShowDeployDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Choose Deployment Type</AlertDialogTitle>
            <AlertDialogDescription>
              Select how you want to deploy your database
            </AlertDialogDescription>
          </AlertDialogHeader>
          <div className="space-y-4 py-4">
            {/* Deployment Type Selection */}
            {generatedSchema && generatedSchema.dynamodb_tables && generatedSchema.postgres_sql && (
              <div className="space-y-3">
                <Label>Database Type</Label>
                <div className="grid grid-cols-2 gap-3">
                  <Button
                    onClick={() => setDeploymentType('dynamodb')}
                    variant={deploymentType === 'dynamodb' ? 'default' : 'outline'}
                    className={`transition-all duration-300 ${
                      deploymentType === 'dynamodb'
                        ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                        : ''
                    }`}
                  >
                    NoSQL (DynamoDB)
                  </Button>
                  
                  <Button
                    onClick={() => setDeploymentType('supabase')}
                    variant={deploymentType === 'supabase' ? 'default' : 'outline'}
                    className={`transition-all duration-300 ${
                      deploymentType === 'supabase'
                        ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white'
                        : ''
                    }`}
                  >
                    PostgreSQL (Supabase)
                  </Button>
                </div>
              </div>
            )}
            
            <div className="space-y-2">
              <Label htmlFor="database-name">Database Name</Label>
              <Input
                id="database-name"
                placeholder="my-database"
                value={databaseName}
                onChange={(e) => setDatabaseName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !isDeploying) {
                    handleDeploy();
                  }
                }}
                disabled={isDeploying}
              />
              <p className="text-xs text-muted-foreground">
                Use lowercase letters, numbers, and hyphens only
              </p>
            </div>
          </div>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={isDeploying}>Cancel</AlertDialogCancel>
            <AlertDialogAction
              onClick={handleDeploy}
              disabled={isDeploying || !databaseName.trim()}
              className="bg-gradient-to-r from-primary to-accent"
            >
              {isDeploying ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deploying...
                </>
              ) : (
                <>
                  <Rocket className="mr-2 h-4 w-4" />
                  Deploy
                </>
              )}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
};

export default Chat;

