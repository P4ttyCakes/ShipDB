import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, Loader2, ZoomIn, ZoomOut, Database, X, FileText } from "lucide-react";

interface Message {
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

const Chat = () => {
  const [message, setMessage] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);
  const [chatWidth, setChatWidth] = useState(30); // Percentage
  const [isResizing, setIsResizing] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [panOffset, setPanOffset] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [schema, setSchema] = useState<any>(null);
  const [isGeneratingSchema, setIsGeneratingSchema] = useState(false);
  const [generatedSchema, setGeneratedSchema] = useState<any>(null);
  const [showSchemaModal, setShowSchemaModal] = useState(false);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Start the conversation when component mounts
    startConversation();
  }, []);

  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      if (!isResizing) return;
      const newWidth = (e.clientX / window.innerWidth) * 100;
      if (newWidth >= 20 && newWidth <= 60) {
        setChatWidth(newWidth);
      }
    };

    const handleMouseUp = () => {
      setIsResizing(false);
    };

    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isResizing]);

  const startConversation = async () => {
    setIsLoading(true);
    try {
      const response = await fetch("http://localhost:8000/api/projects/new_project/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: "My Database Project",
          description: "A new database project",
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to start conversation");
      }

      const data = await response.json();
      setSessionId(data.session_id);
      
      // Add the initial AI message
      setMessages([
        {
          role: "assistant",
          content: data.prompt,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error("Error starting conversation:", error);
      setMessages([
        {
          role: "assistant",
          content: "I apologize, but I'm having trouble connecting to the server. Please make sure the backend is running on port 8000.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async () => {
    if (!message.trim() || isLoading || !sessionId || isDone) return;

    const userMessage: Message = {
      role: "user",
      content: message,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
      setMessage("");
    setIsLoading(true);

    try {
      const response = await fetch("http://localhost:8000/api/projects/new_project/next", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          answer: userMessage.content,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to send message");
      }

      const data = await response.json();

      const aiMessage: Message = {
        role: "assistant",
        content: data.prompt,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, aiMessage]);

      if (data.done) {
        setIsDone(true);
        // Optionally finish the conversation and get the final spec
        finishConversation();
      }
    } catch (error) {
      console.error("Error sending message:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I apologize, but I encountered an error. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const finishConversation = async () => {
    if (!sessionId) return;

    try {
      const response = await fetch("http://localhost:8000/api/projects/new_project/finish", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        console.log("Final spec:", data.spec);
        // Store the spec for schema generation
        setSchema(data.spec);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "Perfect! I've created your database schema. You can now generate the SQL schema using the button below.",
            timestamp: new Date(),
          },
        ]);
      }
    } catch (error) {
      console.error("Error finishing conversation:", error);
    }
  };

  const generateSchema = async () => {
    setIsGeneratingSchema(true);
    
    // If no schema yet, finish the conversation first to get the spec
    if (!schema && sessionId && !isDone) {
      try {
        await finishConversation();
        // Wait a bit for finishConversation to complete
        await new Promise(resolve => setTimeout(resolve, 500));
      } catch (error) {
        console.error("Error finishing conversation:", error);
        setIsGeneratingSchema(false);
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            content: "I had trouble generating the schema. Please try again or continue the conversation.",
            timestamp: new Date(),
          },
        ]);
        return;
      }
    }
    
    // Use the schema if available, otherwise use a default/empty spec
    const specToUse = schema || {
      entities: [
        {
          name: "temp_table",
          fields: [
            { name: "id", type: "integer", primary_key: true },
            { name: "created_at", type: "datetime" }
          ]
        }
      ]
    };

    if (!schema) {
      console.log("Generating with temporary schema since conversation not completed");
    }
    try {
      const response = await fetch("http://localhost:8000/api/schema/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(specToUse),
      });

      if (!response.ok) {
        throw new Error("Failed to generate schema");
      }

      const data = await response.json();
      console.log("Generated schema:", data);
      setGeneratedSchema(data);
      
      // Add success message
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: `Schema generated successfully! Generated ${data.dynamodb_tables?.length || 0} DynamoDB tables and PostgreSQL SQL. Click the schema icon in the top-left to view it.`,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      console.error("Error generating schema:", error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "I encountered an error generating the schema. Please try again.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsGeneratingSchema(false);
    }
  };

  return (
    <div className="h-screen bg-gradient-to-b from-background to-muted flex relative overflow-hidden">
      {/* Left Side - Chat */}
      <div 
        className="border-r border-border/30 flex flex-col bg-background relative h-full"
        style={{ width: `${chatWidth}%` }}
      >
        {/* Chat Header */}
        <div className="p-6 border-b border-border/30">
          <h2 className="text-2xl font-bold bg-gradient-to-r from-foreground via-primary to-accent bg-clip-text text-transparent">
            ShipDB Agent
          </h2>
          <p className="text-sm text-muted-foreground mt-1">
            Describe your database and I'll build it
          </p>
        </div>

        {/* Chat Messages Area */}
        <div className="flex-1 p-6 overflow-y-auto min-h-0">
          <div className="space-y-4">
            {messages.map((msg, index) => (
              <div
                key={index}
                className={`flex ${
                  msg.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`max-w-[80%] rounded-lg p-4 ${
                    msg.role === "user"
                      ? "bg-primary text-primary-foreground"
                      : "bg-card border border-border"
                  }`}
                >
                  <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-card border border-border rounded-lg p-4">
                  <Loader2 className="h-5 w-5 animate-spin" />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Chat Input */}
        <div className="p-6 border-t border-border/30 space-y-3 flex-shrink-0">
          <div className="flex gap-3">
            <Input
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
              placeholder={isDone ? "Conversation completed" : "Type your response..."}
              disabled={isLoading || isDone}
              className="flex-1 bg-card border-border/50"
            />
            <Button
              onClick={handleSend}
              disabled={isLoading || !message.trim() || isDone}
              className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
            >
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
              <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          
          {/* Generate Schema Button - Always visible */}
          <Button
            onClick={generateSchema}
            disabled={isGeneratingSchema || isLoading}
            className="w-full bg-gradient-to-r from-primary to-accent hover:opacity-90 relative overflow-hidden group"
          >
            <span className="relative z-10 flex items-center justify-center">
              {isGeneratingSchema ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Generating Schema...
                </>
              ) : (
                <>
                  <Database className="h-4 w-4 mr-2" />
                  {isDone ? "Generate Database Schema" : "Force Generate Schema"}
                </>
              )}
            </span>
            {/* Wave effect on hover */}
            <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000"></div>
            </div>
          </Button>
        </div>
      </div>

      {/* Resizer */}
      <div
        className="w-1 bg-border/30 hover:bg-primary/50 cursor-col-resize absolute top-0 bottom-0 z-10 transition-colors"
        style={{ left: `${chatWidth}%` }}
        onMouseDown={() => setIsResizing(true)}
      />

      {/* Right Side - Database Flowchart */}
      <div 
        ref={chatContainerRef}
        className="relative overflow-hidden h-full"
        style={{ width: `${100 - chatWidth}%` }}
      >
        {/* Schema Viewer - Top Left */}
        {generatedSchema && (
          <div className="absolute top-4 left-4 z-20 pointer-events-auto">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowSchemaModal(true)}
              className="bg-background/80 backdrop-blur-sm hover:bg-background shadow-lg"
            >
              <FileText className="h-4 w-4 mr-2" />
              View Schema
            </Button>
          </div>
        )}

        {/* Zoom Controls */}
        <div className="absolute top-4 right-4 z-20 flex gap-2 pointer-events-auto">
          <Button
            variant="outline"
            size="icon"
            onClick={() => setZoomLevel(prev => Math.min(prev + 0.1, 2))}
          >
            <ZoomIn className="h-4 w-4" />
          </Button>
          <Button
            variant="outline"
            size="icon"
            onClick={() => setZoomLevel(prev => Math.max(prev - 0.1, 0.5))}
          >
            <ZoomOut className="h-4 w-4" />
          </Button>
        </div>

        {/* Schema Modal */}
        {showSchemaModal && generatedSchema && (
          <div className="absolute inset-0 z-30 bg-background/95 backdrop-blur-sm flex items-center justify-center pointer-events-auto">
            <div className="relative w-full h-full max-w-4xl max-h-[90vh] m-4 bg-card border border-border rounded-lg shadow-xl overflow-hidden flex flex-col">
              {/* Modal Header */}
              <div className="flex items-center justify-between p-4 border-b border-border">
                <h3 className="text-xl font-bold">Generated Database Schema</h3>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => setShowSchemaModal(false)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>

              {/* Modal Content */}
              <div className="flex-1 overflow-auto p-6 space-y-6">
                {/* PostgreSQL SQL */}
                {generatedSchema.postgres_sql && (
                  <div>
                    <h4 className="text-lg font-semibold mb-2 text-primary">PostgreSQL SQL</h4>
                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                      {generatedSchema.postgres_sql}
                    </pre>
                  </div>
                )}

                {/* DynamoDB Tables */}
                {generatedSchema.dynamodb_tables && generatedSchema.dynamodb_tables.length > 0 && (
                  <div>
                    <h4 className="text-lg font-semibold mb-2 text-primary">DynamoDB Tables ({generatedSchema.dynamodb_tables.length})</h4>
                    <div className="space-y-2">
                      {generatedSchema.dynamodb_tables.map((table: any, idx: number) => (
                        <div key={idx} className="bg-muted p-4 rounded-lg">
                          <p className="font-semibold mb-1">{table.TableName}</p>
                          <pre className="text-xs overflow-x-auto">
                            {JSON.stringify(table, null, 2)}
                          </pre>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* JSON Schema */}
                {generatedSchema.json_schema && (
                  <div>
                    <h4 className="text-lg font-semibold mb-2 text-primary">JSON Schema</h4>
                    <pre className="bg-muted p-4 rounded-lg overflow-x-auto text-xs">
                      {JSON.stringify(generatedSchema.json_schema, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Interactive Area for Pan/Zoom */}
        <div 
          className={`absolute inset-0 ${isDragging ? 'cursor-grabbing' : 'cursor-grab'}`}
          onWheel={(e) => {
            if ((e.target as HTMLElement).closest('.pointer-events-auto')) return;
            e.preventDefault();
            const delta = e.deltaY > 0 ? -0.1 : 0.1;
            setZoomLevel(prev => Math.max(0.5, Math.min(2, prev + delta)));
          }}
          onMouseDown={(e) => {
            if ((e.target as HTMLElement).closest('.pointer-events-auto')) return;
            if (e.button === 0 && !isDragging) {
              setIsDragging(true);
              setDragStart({ x: e.clientX - panOffset.x, y: e.clientY - panOffset.y });
            }
          }}
          onMouseMove={(e) => {
            if (isDragging) {
              setPanOffset({
                x: e.clientX - dragStart.x,
                y: e.clientY - dragStart.y
              });
            }
          }}
          onMouseUp={() => setIsDragging(false)}
          onMouseLeave={() => setIsDragging(false)}
        />

        {/* Pannable Content Area */}
        <div 
          className="flex items-center justify-center p-6 relative min-h-full"
          style={{
            transform: `translate(${panOffset.x}px, ${panOffset.y}px) scale(${zoomLevel})`,
            transformOrigin: 'top left',
            width: `${100 / zoomLevel}%`,
            height: `${100 / zoomLevel}%`,
            pointerEvents: 'none'
          }}
        >
          {/* Dotted background pattern */}
          <div 
            className="absolute inset-0 opacity-20"
            style={{
              backgroundImage: `
                radial-gradient(circle, currentColor 1px, transparent 1px)
              `,
              backgroundSize: '40px 40px',
              backgroundPosition: '0 0'
            }}
          />
          <div className="text-center text-muted-foreground relative z-10">
          <p className="text-lg">Database flowchart will appear here</p>
            {isDone && (
              <p className="text-sm mt-2 text-primary">Database schema is ready!</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Chat;
