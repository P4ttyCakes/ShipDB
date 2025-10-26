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
    <div className="h-full w-full flex flex-col">
      <div className="mb-3 pb-3 border-b">
        <h3 className="text-lg font-semibold">Database Schema Visualization</h3>
        <p className="text-sm text-muted-foreground">Interactive ER diagram - drag tables to rearrange</p>
      </div>
      
      <div className="flex-1 overflow-hidden">
        <InteractiveSchemaVisualization schema={schemaData} />
      </div>

      <div className="mt-3 pt-3 border-t text-xs text-muted-foreground bg-muted/50 p-2 rounded">
        <p className="font-semibold text-foreground mb-1">💡 Use:</p>
        <p className="inline mr-2">• Drag tables</p>
        <p className="inline mr-2">• Edit with <Pencil className="inline h-3 w-3 mx-1" /> icon</p>
        <p className="inline mr-2">• Animated arrows show relationships</p>
        <p className="inline">• Zoom controls in bottom left</p>
      </div>
    </div>
  );
});

ChartDBViewer.displayName = 'ChartDBViewer';
