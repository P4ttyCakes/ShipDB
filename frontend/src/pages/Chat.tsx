import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Send, Loader2, Maximize2, Rocket } from "lucide-react";
import { toast } from "sonner";
import { ChartDBViewer, ChartDBViewerRef } from "@/components/ChartDBViewer";
import { TypewriterText } from "@/components/TypewriterText";
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
  const [completedMessages, setCompletedMessages] = useState<Set<number>>(new Set());
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chartDBViewerRef = useRef<ChartDBViewerRef>(null);
  const scrollTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const throttledScroll = () => {
    if (scrollTimeoutRef.current) {
      clearTimeout(scrollTimeoutRef.current);
    }
    scrollTimeoutRef.current = setTimeout(() => {
      scrollToBottom();
    }, 100); // Throttle to every 100ms
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, completedMessages]);

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
          let errorMessage = '';
          let errorDetail = '';
          try {
            const errorData = await response.json();
            errorDetail = errorData.detail || '';
          } catch {
            // If response is not JSON, use the status text
            errorDetail = response.statusText || 'Unknown error';
          }
          
          // Create user-friendly error messages based on status code and detail
          if (response.status === 400) {
            if (errorDetail.includes('required') || errorDetail.includes('invalid')) {
              errorMessage = `Invalid request: ${errorDetail}`;
            } else if (errorDetail.includes('JSON') || errorDetail.includes('parse')) {
              errorMessage = `The AI service returned an invalid response. Please try again. Details: ${errorDetail}`;
            } else {
              errorMessage = `Invalid input: ${errorDetail}`;
            }
          } else if (response.status === 500) {
            if (errorDetail.includes('unavailable') || errorDetail.includes('retries')) {
              errorMessage = `Service temporarily unavailable: ${errorDetail}`;
            } else if (errorDetail.includes('JSON') || errorDetail.includes('parse')) {
              errorMessage = `The AI service had trouble processing your response. Please try rephrasing your answer. Details: ${errorDetail}`;
            } else {
              errorMessage = `Server error (${response.status}): ${errorDetail || 'An unexpected error occurred. Please try again.'}`;
            }
          } else {
            errorMessage = `Error (${response.status}): ${errorDetail || response.statusText || 'Unknown error'}`;
          }
          
          throw new Error(errorMessage);
        }

        const result = await response.json();
        console.log('Start conversation result:', result); // Debug log
        setSessionId(result.session_id);
        setMessages([{ role: 'assistant', content: result.prompt }]);
        setInitializing(false);
      } catch (error) {
        console.error('Error starting conversation:', error); // Debug log
        const errorMessage = error instanceof Error ? error.message : 'Unknown error';
        toast.error(`Failed to start conversation: ${errorMessage}`);
        setMessages([{ role: 'assistant', content: `I couldn't start the conversation. ${errorMessage}. Please refresh the page or try again.` }]);
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
        let errorMessage = '';
        let errorDetail = '';
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || '';
        } catch {
          // If response is not JSON, use the status text
          errorDetail = response.statusText || 'Unknown error';
        }
        
        // Create user-friendly error messages based on status code and detail
        if (response.status === 400) {
          if (errorDetail.includes('required') || errorDetail.includes('invalid session')) {
            errorMessage = `Invalid request: ${errorDetail}. Please refresh the page and try again.`;
          } else if (errorDetail.includes('JSON') || errorDetail.includes('parse') || errorDetail.includes('invalid response')) {
            errorMessage = `The AI service had trouble understanding your response. Please try rephrasing your answer or providing more details. Error: ${errorDetail}`;
          } else if (errorDetail.includes("doesn't fit") || errorDetail.includes("not match") || errorDetail.includes("does not match")) {
            errorMessage = `Your answer doesn't match what was asked. ${errorDetail}. Please read the question carefully and try again.`;
          } else {
            errorMessage = `Invalid input: ${errorDetail}`;
          }
        } else if (response.status === 500) {
          if (errorDetail.includes('unavailable') || errorDetail.includes('retries')) {
            errorMessage = `AI service temporarily unavailable: ${errorDetail}. Please wait a moment and try again.`;
          } else if (errorDetail.includes('JSON') || errorDetail.includes('parse') || errorDetail.includes('invalid response')) {
            errorMessage = `The AI service had trouble processing your response. Please try rephrasing your answer or providing more context. Error: ${errorDetail}`;
          } else {
            errorMessage = `Server error: ${errorDetail || 'An unexpected error occurred. Please try again.'}`;
          }
        } else {
          errorMessage = `Error (${response.status}): ${errorDetail || response.statusText || 'Unknown error'}`;
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      console.log('Chat result:', result); // Debug logging
      const newMessageIndex = messages.length + 1; // +1 for user message, +1 for assistant
      setMessages(prev => [...prev, { role: 'assistant', content: result.prompt }]);
      // Don't mark as completed immediately - let typewriter handle it
      
      if (result.done) {
        console.log('Conversation marked as done'); // Debug logging
        setConversationDone(true);
        toast.success("Conversation complete! You can finish to generate the schema.");
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      toast.error(`Failed to process your message: ${errorMessage}`);
      setMessages(prev => [...prev, { role: 'assistant', content: `I couldn't process your response. ${errorMessage}. Please try again with a different answer.` }]);
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
        let errorMessage = '';
        let errorDetail = '';
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || '';
        } catch {
          // If response is not JSON, use the status text
          errorDetail = response.statusText || 'Unknown error';
        }
        
        // Create user-friendly error messages based on status code and detail
        if (response.status === 400) {
          if (errorDetail.includes('required') || errorDetail.includes('invalid session')) {
            errorMessage = `Invalid request: ${errorDetail}. Please refresh the page and try again.`;
          } else if (errorDetail.includes('JSON') || errorDetail.includes('parse') || errorDetail.includes('invalid response')) {
            errorMessage = `The AI service had trouble understanding your response. Please try rephrasing your answer or providing more details. Error: ${errorDetail}`;
          } else if (errorDetail.includes("doesn't fit") || errorDetail.includes("not match") || errorDetail.includes("does not match")) {
            errorMessage = `Your answer doesn't match what was asked. ${errorDetail}. Please read the question carefully and try again.`;
          } else {
            errorMessage = `Invalid input: ${errorDetail}`;
          }
        } else if (response.status === 500) {
          if (errorDetail.includes('unavailable') || errorDetail.includes('retries')) {
            errorMessage = `AI service temporarily unavailable: ${errorDetail}. Please wait a moment and try again.`;
          } else if (errorDetail.includes('JSON') || errorDetail.includes('parse') || errorDetail.includes('invalid response')) {
            errorMessage = `The AI service had trouble processing your response. Please try rephrasing your answer or providing more context. Error: ${errorDetail}`;
          } else {
            errorMessage = `Server error: ${errorDetail || 'An unexpected error occurred. Please try again.'}`;
          }
        } else {
          errorMessage = `Error (${response.status}): ${errorDetail || response.statusText || 'Unknown error'}`;
        }
        
        throw new Error(errorMessage);
      }

      const result = await response.json();
      toast.success("Schema generated successfully!");
      console.log("Generated spec:", result.spec);
      
      // Store the generated schema
      setGeneratedSchema(result.spec);
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      toast.error(`Failed to generate schema: ${errorMessage}`);
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
    <div className="h-screen bg-background flex overflow-hidden">
      {/* Left Side - Chat */}
      <div 
        className="border-r border-border/30 flex flex-col overflow-hidden"
        style={{ width: `${leftWidth}%` }}
      >
        {/* Chat Header */}
        <div className="p-6 border-b border-border bg-card">
          <h2 className="text-2xl font-bold text-foreground">
            ShipDB Agent
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Describe your database and I'll build it
          </p>
        </div>

        {/* Chat Messages Area */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4">
          {messages.length === 0 && initializing && (
            <div className="text-center text-muted-foreground mt-8">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
              <p className="text-lg">Starting conversation...</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-4 ${
                  msg.role === 'user'
                    ? 'bg-primary text-primary-foreground'
                    : 'bg-card border border-border/50'
                }`}
              >
                {msg.role === 'assistant' && !completedMessages.has(idx) ? (
                  <p className="text-sm">
                    <TypewriterText 
                      text={msg.content} 
                      speed={15}
                      onComplete={() => {
                        setCompletedMessages(prev => new Set([...prev, idx]));
                        scrollToBottom();
                      }}
                      onUpdate={throttledScroll}
                    />
                  </p>
                ) : (
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-card border border-border/50 rounded-lg p-4">
                <Loader2 className="h-4 w-4 animate-spin" />
              </div>
            </div>
          )}
          
          
          <div ref={messagesEndRef} />
        </div>

        {/* Chat Input */}
        <div className="p-6 border-t border-border bg-card space-y-3">
          {conversationDone && (
            <Button
              onClick={handleFinish}
              disabled={isLoading}
              className="w-full bg-primary hover:bg-primary/85 shadow-md"
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
          
          <div className="flex gap-3">
            <Input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !isLoading && !initializing && handleSend()}
              placeholder={initializing ? "Starting conversation..." : "Answer the question..."}
              className="flex-1 bg-card border-border/50"
              disabled={isLoading || initializing}
            />
            <Button
              onClick={handleSend}
              disabled={isLoading || initializing || !input.trim()}
              className="bg-primary hover:bg-primary/85 shadow-md"
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

      {/* Draggable Divider */}
      <div
        className="w-1 bg-border/50 hover:bg-border cursor-col-resize transition-colors relative group"
        onMouseDown={() => setIsDragging(true)}
      >
        <div className="absolute inset-y-0 left-1/2 -translate-x-1/2 w-4 flex items-center justify-center">
          <div className="w-1 h-12 bg-border rounded-full group-hover:bg-accent transition-colors" />
        </div>
      </div>

      {/* Right Side - ChartDB Visualization */}
      <div 
        className="flex flex-col p-6 overflow-hidden flex-1"
        style={{ width: `${100 - leftWidth}%`, minWidth: 0 }}
      >
        {generatedSchema ? (
          <div className="flex-1 flex flex-col overflow-hidden space-y-3">
            {/* Schema Info - Compact */}
            <div className="flex items-center gap-3 flex-shrink-0">
              <Button
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
                onClick={() => setShowSchemaModal(true)}
              >
                <Maximize2 className="h-4 w-4" />
                <span className="text-xs">Schema</span>
                <span className="text-xs text-muted-foreground">({generatedSchema.entities?.length || 0})</span>
              </Button>
              
              {/* Deploy Button - Next to Schema */}
              {(generatedSchema.dynamodb_tables?.length > 0 || generatedSchema.postgres_sql) && (
                <Button
                  onClick={() => setShowDeployDialog(true)}
                  className="bg-primary hover:bg-primary/85 shadow-md"
                  size="sm"
                >
                  <Rocket className="h-4 w-4 mr-2" />
                  <span className="text-xs">Deploy</span>
                </Button>
              )}
            </div>

            {/* ChartDB Visualization */}
            <div className="flex-1 overflow-hidden relative" style={{ minWidth: 0 }}>
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
          <div className="flex items-center justify-center h-full">
            <div className="text-center text-muted-foreground">
              <p className="text-lg">Complete the conversation to generate your database schema</p>
              <p className="text-sm mt-2">The visualization will appear automatically here</p>
            </div>
          </div>
        )}
      </div>

      {/* Schema Modal */}
      <Dialog open={showSchemaModal} onOpenChange={setShowSchemaModal}>
        <DialogContent className="max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
          <DialogHeader>
            <DialogTitle>Database Schema - {generatedSchema?.app_type || 'Database'}</DialogTitle>
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
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono">
                    {generatedSchema.postgres_sql}
                  </pre>
                ) : (
                  <p className="text-muted-foreground">PostgreSQL schema not yet generated.</p>
                )}
              </TabsContent>

              <TabsContent value="json" className="flex-1 overflow-y-auto mt-4">
                {generatedSchema.json_schema ? (
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono">
                    {JSON.stringify(generatedSchema.json_schema, null, 2)}
                  </pre>
                ) : (
                  <p className="text-muted-foreground">JSON schema not yet generated.</p>
                )}
              </TabsContent>

              <TabsContent value="dynamodb" className="flex-1 overflow-y-auto mt-4">
                {generatedSchema.dynamodb_tables ? (
                  <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-sm font-mono">
                    {JSON.stringify(generatedSchema.dynamodb_tables, null, 2)}
                  </pre>
                ) : (
                  <p className="text-muted-foreground">DynamoDB schema not yet generated.</p>
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
                    variant="outline"
                    className={deploymentType === 'dynamodb' ? 'bg-muted' : ''}
                  >
                    NoSQL (DynamoDB)
                  </Button>
                  
                  <Button
                    onClick={() => setDeploymentType('supabase')}
                    variant="outline"
                    className={deploymentType === 'supabase' ? 'bg-muted' : ''}
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
              className="bg-primary hover:bg-primary/85 shadow-md"
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
