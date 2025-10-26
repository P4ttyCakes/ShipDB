import { useState, useImperativeHandle, forwardRef } from 'react';
import { Loader2, AlertCircle, Pencil } from 'lucide-react';
import { toast } from 'sonner';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { InteractiveSchemaVisualization } from '@/components/InteractiveSchemaVisualization';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ChartDBViewerProps {
  projectId: string;
  deploymentType: 'supabase' | 'postgresql';
  onSchemaUpdate?: (updatedSchema: any) => void;
}

export interface ChartDBViewerRef {
  loadSchema: (spec: any) => Promise<void>;
}

interface AnthropicConfig {
  anthropic_api_key: string;
  anthropic_endpoint: string;
  anthropic_model: string;
}

export const ChartDBViewer = forwardRef<ChartDBViewerRef, ChartDBViewerProps>(({ projectId, deploymentType, onSchemaUpdate }, ref) => {
  const [loading, setLoading] = useState(false);
  const [schemaData, setSchemaData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSchemaUpdate = async (updatedSchema: any) => {
    try {
      // Update the schema via API
      const response = await fetch(`${API_BASE_URL}/api/schema/update`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project_id: projectId,
          schema: updatedSchema,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update schema');
      }

      const result = await response.json();
      
      // Get the updated artifacts from the response
      const updatedSchemaWithArtifacts = {
        ...updatedSchema,
        ...result.artifacts, // Include postgres_sql, json_schema, dynamodb_tables
      };

      // Update local state with full schema including artifacts
      setSchemaData(updatedSchemaWithArtifacts);
      
      // Call parent's onSchemaUpdate with the complete updated schema
      if (onSchemaUpdate) {
        onSchemaUpdate(updatedSchemaWithArtifacts);
      }
      
      toast.success('Schema updated successfully');
    } catch (error) {
      console.error('Error updating schema:', error);
      toast.error('Failed to update schema');
    }
  };

  const loadSchema = async (spec: any) => {
    setLoading(true);
    setError(null);
    try {
      // Store the schema data for visualization
      setSchemaData(spec);
      toast.success('Schema visualization loaded');
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      setError(`Failed to load visualization: ${errorMsg}`);
      console.error('Visualization error:', error);
    } finally {
      setLoading(false);
    }
  };

  // Expose loadSchema method to parent via ref
  useImperativeHandle(ref, () => ({
    loadSchema
  }));


  // Don't show anything until schema is loaded
  if (!schemaData && !loading && !error) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center text-muted-foreground">
          <p className="text-sm">Schema visualization will appear here</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8">
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading visualization...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full w-full flex flex-col" style={{ minWidth: 0 }}>
      <div className="flex-1 overflow-hidden min-w-0" style={{ minHeight: 0 }}>
        <InteractiveSchemaVisualization 
          schema={schemaData} 
          onSchemaUpdate={handleSchemaUpdate}
        />
      </div>

      <div className="px-2 py-1 border-t text-xs text-muted-foreground bg-muted/50 flex items-center gap-2">
        <span>💡</span>
        <span>Drag to move • Edit text • Resize corners • Scroll fields</span>
      </div>
    </div>
  );
});

ChartDBViewer.displayName = 'ChartDBViewer';
