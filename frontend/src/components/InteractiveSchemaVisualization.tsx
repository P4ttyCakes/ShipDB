import { useState, useCallback, useEffect } from 'react';
import {
  ReactFlow,
  Node,
  Edge,
  Controls,
  Background,
  NodeTypes,
  BackgroundVariant,
  NodeProps,
  Handle,
  Position,
  Connection,
  useNodesState,
  useEdgesState,
  NodeResizer,
  addEdge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Trash2, Plus, Sparkles } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface Field {
  name: string;
  type: string;
  primaryKey?: boolean;
  foreignKey?: any;
  required?: boolean;
}

interface Table {
  name: string;
  fields: Field[];
  x?: number;
  y?: number;
  width?: number;
  height?: number;
}

interface InteractiveSchemaVisualizationProps {
  schema: any;
  onSchemaUpdate?: (updatedSchema: any) => void;
}

interface TableNodeData {
  tableName?: string;
  fields?: any[];
  color?: {
    bg: string;
    border: string;
    text: string;
  };
  onSizeChange?: (id: string, width: number, height: number) => void;
  onConnect?: (sourceNodeId: string, targetNodeId: string) => void;
  onFieldsChange?: (nodeId: string, fields: any[]) => void;
  allTables?: Array<{ id: string; name: string }>;
  currentNodeId?: string;
  isSuggestion?: boolean;
}

// Color palette for tables sharing common entities - VIBRANT BORDER COLORS
const colorPalette = [
  { bg: 'hsl(var(--card))', border: 'hsl(195 75% 50%)', text: 'hsl(var(--foreground))' }, // Blue
  { bg: 'hsl(var(--card))', border: 'hsl(142 70% 50%)', text: 'hsl(var(--foreground))' }, // Green
  { bg: 'hsl(var(--card))', border: 'hsl(338 70% 60%)', text: 'hsl(var(--foreground))' }, // Pink
  { bg: 'hsl(var(--card))', border: 'hsl(262 70% 60%)', text: 'hsl(var(--foreground))' }, // Purple
  { bg: 'hsl(var(--card))', border: 'hsl(346 70% 60%)', text: 'hsl(var(--foreground))' }, // Rose
  { bg: 'hsl(var(--card))', border: 'hsl(221 70% 60%)', text: 'hsl(var(--foreground))' }, // Indigo
  { bg: 'hsl(var(--card))', border: 'hsl(152 70% 50%)', text: 'hsl(var(--foreground))' }, // Emerald
  { bg: 'hsl(var(--card))', border: 'hsl(261 70% 60%)', text: 'hsl(var(--foreground))' }, // Violet
];

const TableNode = (props: NodeProps) => {
  const data = props.data as TableNodeData;
  const [isEditingTableName, setIsEditingTableName] = useState(false);
  const [tableName, setTableName] = useState(data?.tableName || '');
  const [fields, setFields] = useState<any[]>(Array.isArray(data?.fields) ? data.fields : []);
  const [editingField, setEditingField] = useState<number | null>(null);
  const [editingType, setEditingType] = useState<number | null>(null);
  const [nameError, setNameError] = useState<string | null>(null);

  // Update fields when data changes from parent
  useEffect(() => {
    if (Array.isArray(data?.fields)) {
      setFields(data.fields);
    }
  }, [data?.fields]);

  const handleAddField = () => {
    const newField = { name: `field_${fields.length + 1}`, type: 'text', primaryKey: false, required: false };
    const updatedFields = [...fields, newField];
    setFields(updatedFields);
    setEditingField(fields.length);
    
    // Auto-resize based on field count
    const fieldCount = updatedFields.length;
    const dynamicHeight = Math.max(200, 120 + fieldCount * 32);
    
    if (data?.onSizeChange) {
      data.onSizeChange(props.id as string, width, dynamicHeight);
    }
    
    // Notify parent that fields have changed
    if (data?.onFieldsChange) {
      data.onFieldsChange(props.id as string, updatedFields);
    }
  };

  const handleRemoveField = (index: number) => {
    const updatedFields = fields.filter((_: any, i: number) => i !== index);
    setFields(updatedFields);
    
    // Auto-resize based on field count
    const fieldCount = updatedFields.length;
    const dynamicHeight = Math.max(200, 120 + fieldCount * 32);
    
    if (data?.onSizeChange) {
      data.onSizeChange(props.id as string, width, dynamicHeight);
    }
    
    // Notify parent that fields have changed
    if (data?.onFieldsChange) {
      data.onFieldsChange(props.id as string, updatedFields);
    }
  };

  const handleUpdateField = (index: number, updates: any) => {
    const updatedFields = fields.map((field: any, i: number) => (i === index ? { ...field, ...updates } : field));
    setFields(updatedFields);
    
    // Notify parent that fields have changed
    if (data?.onFieldsChange) {
      data.onFieldsChange(props.id as string, updatedFields);
    }
  };

  const bgColor = data?.color?.bg || 'hsl(var(--card))';
  const borderColor = data?.color?.border || 'hsl(var(--border))';
  const textColor = data?.color?.text || 'hsl(var(--foreground))';
  
  const width = props.width || 300;
  const height = props.height || 400;
  const isSuggestion = data?.isSuggestion || false;

  return (
    <div 
      className="rounded-lg shadow-xl relative overflow-hidden"
      style={{ 
        backgroundColor: bgColor,
        border: `3px solid ${borderColor}`,
        width: width,
        height: height,
        minWidth: 250,
        minHeight: 200,
      }}
    >
      {/* Custom Resize Handle - Bottom Right - Hidden for suggestions */}
      {!isSuggestion && (
      <div
        className="absolute bottom-0 right-0 w-6 h-6 cursor-nwse-resize z-50 bg-blue-500 border-2 border-white rounded-tl-lg hover:bg-blue-600 transition-colors"
        style={{
          clipPath: 'polygon(100% 0, 100% 100%, 0 100%)',
        }}
        onMouseDown={(e) => {
          e.stopPropagation();
          const startX = e.clientX;
          const startY = e.clientY;
          const startWidth = width;
          const startHeight = height;

          const handleMouseMove = (moveEvent: MouseEvent) => {
            const deltaX = moveEvent.clientX - startX;
            const deltaY = moveEvent.clientY - startY;
            
            let newWidth = startWidth + deltaX;
            let newHeight = startHeight + deltaY;
            
            newWidth = Math.max(250, Math.min(800, newWidth));
            newHeight = Math.max(200, Math.min(1200, newHeight));
            
            // Call the parent's callback to update node size
            if (data?.onSizeChange) {
              data.onSizeChange(props.id as string, newWidth, newHeight);
            }
          };

          const handleMouseUp = () => {
            document.removeEventListener('mousemove', handleMouseMove);
            document.removeEventListener('mouseup', handleMouseUp);
          };

          document.addEventListener('mousemove', handleMouseMove);
          document.addEventListener('mouseup', handleMouseUp);
        }}
      />
      )}
      
      <Handle 
        type="source" 
        position={Position.Right} 
        id="right"
        style={{ width: '12px', height: '12px', right: '-6px', backgroundColor: borderColor, border: '2px solid white' }}
      />
      <Handle 
        type="target" 
        position={Position.Left} 
        id="left"
        style={{ width: '12px', height: '12px', left: '-6px', backgroundColor: borderColor, border: '2px solid white' }}
      />
      <Handle 
        type="source" 
        position={Position.Bottom} 
        id="bottom"
        style={{ width: '12px', height: '12px', bottom: '-6px', backgroundColor: borderColor, border: '2px solid white' }}
      />
      <Handle 
        type="target" 
        position={Position.Top} 
        id="top"
        style={{ width: '12px', height: '12px', top: '-6px', backgroundColor: borderColor, border: '2px solid white' }}
      />
      
      {/* Colored Header Bar - Thick and Visible */}
      <div 
        className="h-2 w-full"
        style={{ 
          backgroundColor: borderColor,
        }}
      />
      
      {/* Table Header */}
      <div 
        className="p-3 border-b-2 shadow-sm" 
        style={{ 
          borderColor: `${borderColor}80`,
          backgroundColor: bgColor,
        }}
      >
        <div className="flex items-center justify-between gap-2">
          {isEditingTableName ? (
            <Input
              value={tableName}
              onChange={(e) => setTableName(e.target.value)}
              onBlur={() => setIsEditingTableName(false)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') setIsEditingTableName(false);
              }}
              className="text-sm font-bold flex-1"
              placeholder="Table name"
              autoFocus
            />
          ) : (
            <h3 
              className="font-bold text-lg capitalize truncate flex-1 cursor-pointer hover:opacity-80 transition-opacity"
              onClick={() => setIsEditingTableName(true)}
              style={{ color: textColor }}
            >
              {tableName}
            </h3>
          )}

        </div>
      </div>
      
      {/* Fields - Always Scrollable */}
      <div className="p-2 pb-1 space-y-1 h-[calc(100%-6.5rem)] overflow-y-auto overscroll-contain">
            {fields.map((field: any, idx: number) => (
          <div key={idx}>
            <div 
              className={`flex items-center gap-2 text-xs py-1 px-2 rounded hover:bg-black/5 transition-colors ${
                editingField === idx || editingType === idx ? 'bg-primary/10' : ''
              }`}
            >
            {editingField === idx ? (
                <Input
                value={field.name || ''}
                onChange={(e) => {
                  const newName = e.target.value;
                  handleUpdateField(idx, { name: newName });
                  if (!newName.trim()) {
                    setNameError('Field name is required');
                  } else {
                    setNameError(null);
                  }
                }}
                placeholder="Field name (required)"
                className={`flex-1 h-7 text-xs ${nameError ? 'border-red-500' : ''}`}
                autoFocus
                onBlur={() => {
                  if (!field.name || !field.name.trim()) {
                    setNameError('Please enter a field name');
                  } else {
                    setNameError(null);
                    setEditingField(null);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    if (!field.name || !field.name.trim()) {
                      setNameError('Please enter a field name');
                    } else {
                      setNameError(null);
                      setEditingField(null);
                    }
                  } else if (e.key === 'Escape') {
                    setNameError(null);
                    setEditingField(null);
                  }
                }}
              />
            ) : (
              <span 
                className={`font-mono flex-1 cursor-pointer hover:opacity-80 transition-opacity ${field.primaryKey ? 'font-bold' : ''}`}
                onClick={() => setEditingField(idx)}
                style={{ color: field.primaryKey ? 'hsl(var(--primary))' : 'hsl(var(--foreground))' }}
              >
                {field.name || <span className="text-red-500 italic">(no name)</span>}
              </span>
            )}
            
            {editingType === idx ? (
                <Input
                value={field.type || ''}
                  onChange={(e) => handleUpdateField(idx, { type: e.target.value })}
                placeholder="Type (required)"
                className={`w-24 h-7 text-xs ${!field.type || !field.type.trim() ? 'border-red-500' : ''}`}
                autoFocus
                onBlur={() => {
                  if (!field.type || !field.type.trim()) {
                    handleUpdateField(idx, { type: 'text' });
                    setNameError('Type is required');
                  } else {
                    setNameError(null);
                    setEditingType(null);
                  }
                }}
                onKeyDown={(e) => {
                  if (e.key === 'Enter') {
                    if (!field.type || !field.type.trim()) {
                      handleUpdateField(idx, { type: 'text' });
                      setNameError('Type is required');
                    } else {
                      setNameError(null);
                      setEditingType(null);
                    }
                  } else if (e.key === 'Escape') {
                    setNameError(null);
                    setEditingType(null);
                  }
                }}
              />
            ) : (
              <span 
                className="text-xs bg-muted px-2 py-0.5 rounded cursor-pointer hover:opacity-80 transition-opacity" 
                style={{ color: 'hsl(var(--muted-foreground))' }}
                onClick={() => setEditingType(idx)}
              >
                {field.type}
              </span>
            )}
            
            {editingField !== idx && editingType !== idx && (
              <>
                {field.primaryKey && (
                  <span className="text-xs bg-blue-500/20 text-blue-600 px-2 py-0.5 rounded">PK</span>
                )}
                {field.foreign_key && (
                  <span className="text-xs bg-green-500/20 text-green-600 px-2 py-0.5 rounded">FK</span>
                )}
                {!field.required && (
                  <span className="text-xs bg-orange-500/20 text-orange-600 px-2 py-0.5 rounded">NULL</span>
                )}
              </>
            )}
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleRemoveField(idx)}
              className="h-6 w-6 p-0 hover:bg-destructive/10 hover:text-destructive"
                >
              <Trash2 className="h-3 w-3" />
                </Button>
            </div>
            {nameError && (editingField === idx || editingType === idx) && (
              <div className="text-xs text-red-500 px-2 pb-1">
                {nameError}
              </div>
            )}
              </div>
            ))}
      </div>
      
      {/* Add Field Button and Connect Dropdown - Fixed at Bottom, Outside Scroll Area */}
      <div className="px-2 pb-1.5 pt-1.5 border-t flex-shrink-0" style={{ borderColor: `${borderColor}40` }}>
        <div className="grid grid-cols-2 gap-1.5">
            <Button
              size="sm"
              variant="outline"
              onClick={handleAddField}
            className="h-7 text-xs"
            >
            <Plus className="mr-1 h-3 w-3" />
            Add Field
            </Button>
          <Select
            onValueChange={(value) => {
              console.log('Connecting:', data?.currentNodeId, 'to', value);
              if (value && data?.onConnect && data?.currentNodeId) {
                data.onConnect(data.currentNodeId, value);
              }
            }}
          >
            <SelectTrigger className="h-7 text-xs">
              <SelectValue placeholder="Connect..." />
            </SelectTrigger>
            <SelectContent>
              {data?.allTables && data.allTables.length > 0 ? (
                data.allTables.filter(table => table.id !== data?.currentNodeId).map((table) => (
                  <SelectItem key={table.id} value={table.id}>
                    {table.name}
                  </SelectItem>
                ))
              ) : (
                <SelectItem value="none" disabled>No tables available</SelectItem>
              )}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
};

const nodeTypes: NodeTypes = {
  tableNode: TableNode,
};

// Helper function to find tables that share common fields (matching name and type)
const findCommonEntityGroups = (entities: any[]) => {
  // Build a map of field signatures (name:type) to tables that have them
  const fieldSignatures: { [signature: string]: Set<string> } = {};
  
  entities.forEach((entity) => {
    entity.fields?.forEach((field: any) => {
      // Create a signature from field name and type
      const signature = `${field.name}:${field.type}`;
      if (!fieldSignatures[signature]) {
        fieldSignatures[signature] = new Set();
      }
      fieldSignatures[signature].add(entity.name);
    });
  });
  
  // Find field signatures that appear in multiple tables
  const sharedFields = Object.entries(fieldSignatures)
    .filter(([_, tables]) => tables.size > 1);
  
  if (sharedFields.length === 0) {
    return [];
  }
  
  // Build groups: tables that share at least one common field
  const tableGroups = new Map<string, Set<string>>();
  
  sharedFields.forEach(([signature, tables]) => {
    const tablesArray = Array.from(tables);
    const key = tablesArray.sort().join('-');
    
    if (!tableGroups.has(key)) {
      tableGroups.set(key, new Set(tablesArray));
    } else {
      // Merge with existing group
      tablesArray.forEach(table => tableGroups.get(key)!.add(table));
    }
  });
  
  // Convert to array format
  const groups: string[][] = Array.from(tableGroups.values()).map(group => Array.from(group));
  
  return groups;
};

// Hierarchical layout algorithm to reduce edge crossings
const calculateHierarchicalLayout = (entities: any[], edges: Edge[]) => {
  // Find root nodes (nodes with no incoming edges)
  const hasIncoming = new Set<string>();
  edges.forEach((edge) => {
    hasIncoming.add(edge.target as string);
  });
  
  const roots = entities.filter((e) => !hasIncoming.has(e.name));
  
  // Build adjacency list
  const children: { [key: string]: string[] } = {};
  entities.forEach((e) => {
    children[e.name] = [];
  });
  
  edges.forEach((edge) => {
    if (!children[edge.source as string]) {
      children[edge.source as string] = [];
    }
    children[edge.source as string].push(edge.target as string);
  });
  
  // Calculate levels using BFS
  const levels: { [key: string]: number } = {};
  const queue: string[] = [];
  
  roots.forEach((root) => {
    levels[root.name] = 0;
    queue.push(root.name);
  });
  
  while (queue.length > 0) {
    const current = queue.shift()!;
    const currentLevel = levels[current];
    
    children[current]?.forEach((child) => {
      if (levels[child] === undefined || levels[child] > currentLevel + 1) {
        levels[child] = currentLevel + 1;
        queue.push(child);
      }
    });
  }
  
  // Arrange nodes by level
  const maxLevel = Math.max(...Object.values(levels));
  const levelBuckets: string[][] = [];
  for (let i = 0; i <= maxLevel; i++) {
    levelBuckets[i] = [];
  }
  
  entities.forEach((entity) => {
    const level = levels[entity.name] ?? 0;
    levelBuckets[level].push(entity.name);
  });
  
  return levelBuckets;
};

// API function to fetch AI suggestions
const fetchAISuggestions = async (schemaData: any) => {
  try {
    const response = await fetch('http://localhost:8000/api/schema/suggestions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ schema: schemaData }),
    });
    if (!response.ok) throw new Error('Failed to fetch suggestions');
    return await response.json();
  } catch (error) {
    console.error('Error fetching AI suggestions:', error);
    return null;
  }
};

export const InteractiveSchemaVisualization = ({ schema, onSchemaUpdate }: InteractiveSchemaVisualizationProps) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [aiSuggestionsEnabled, setAiSuggestionsEnabled] = useState(false);
  const [aiSuggestions, setAiSuggestions] = useState<any>(null);
  const [activeSuggestionOption, setActiveSuggestionOption] = useState<1 | 2>(1);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [suggestionNodes, setSuggestionNodes] = useState<Node[]>([]);
  const [suggestionEdges, setSuggestionEdges] = useState<Edge[]>([]);
  const [cachedNodes, setCachedNodes] = useState<{ option1: Node[] | null, option2: Node[] | null }>({ option1: null, option2: null });
  const [cachedEdges, setCachedEdges] = useState<{ option1: Edge[] | null, option2: Edge[] | null }>({ option1: null, option2: null });

  // Handler for when nodes request a size change
  const handleNodeSizeChange = useCallback((nodeId: string, width: number, height: number) => {
    setNodes((nds) => {
      const updated = [...nds];
      const index = updated.findIndex((n) => n.id === nodeId);
      if (index !== -1) {
        updated[index] = {
          ...updated[index],
          width,
          height,
          style: {
            ...updated[index].style,
            width,
            height,
          },
        };
      }
      return updated;
    });
  }, []);

  // Handle dropdown-based connections
  const handleConnect = useCallback((sourceNodeId: string, targetNodeId: string) => {
    const edgeId = `${sourceNodeId}-${targetNodeId}-${Date.now()}`;
    const newEdge = {
      id: edgeId,
      source: sourceNodeId,
      target: targetNodeId,
      type: 'straight' as const,
      animated: false,
      markerEnd: {
        type: 'arrowclosed' as const,
        width: 20,
        height: 20,
        color: '#475569',
      },
      style: { 
        stroke: '#475569', 
        strokeWidth: 2,
        opacity: 0.8,
      },
    };
    
    setEdges((eds) => [...eds, newEdge]);
  }, []);

  // Handle field changes to update colors dynamically
  const handleFieldsChange = useCallback((nodeId: string, newFields: any[]) => {
    console.log('handleFieldsChange called for', nodeId, 'with fields:', newFields);
    
    // Update the node's fields and recalculate colors in one go
    setNodes((currentNodes) => {
      // First, update the fields for the changed node
      const updatedNodes = currentNodes.map((node) => 
        node.id === nodeId
          ? { ...node, data: { ...node.data, fields: newFields } }
          : node
      );
      
      // Extract all entities from updated nodes
      const allEntities = updatedNodes.map(node => ({
        name: node.id,
        fields: (node.data as TableNodeData).fields || [],
      }));
      
      console.log('All entities:', allEntities);
      
      // Find common entity groups
      const groups = findCommonEntityGroups(allEntities);
      
      console.log('Groups:', groups);
      
      // Build color map
      const nodeColorMap: { [key: string]: { bg: string; border: string; text: string } } = {};
      groups.forEach((group, groupIndex) => {
        const color = colorPalette[groupIndex % colorPalette.length];
        group.forEach((tableName) => {
          nodeColorMap[tableName] = color;
        });
      });
      
      console.log('Color map:', nodeColorMap);
      
      // Update node colors
      return updatedNodes.map((node) => ({
        ...node,
        data: {
          ...node.data,
          color: nodeColorMap[node.id] || (node.data as TableNodeData).color || colorPalette[0],
        },
      }));
    });
  }, []);

  // Parse schema and create nodes
  useEffect(() => {
    if (!schema?.entities) return;

    // First pass: count relationships to identify important ones
    const relationshipCount: { [key: string]: number } = {};
    
    schema.entities.forEach((entity: any) => {
      entity.fields?.forEach((field: any) => {
        if (field.foreign_key?.table) {
          const key = `${entity.name}<->${field.foreign_key.table}`;
          relationshipCount[key] = (relationshipCount[key] || 0) + 1;
        }
      });
    });
    
    // Second pass: create edges with different styling based on importance
    const initialEdges: Edge[] = [];
    
    schema.entities.forEach((entity: any) => {
      entity.fields?.forEach((field: any) => {
        if (field.foreign_key?.table) {
          const key = `${entity.name}<->${field.foreign_key.table}`;
          const count = relationshipCount[key] || 1;
          const isImportant = count >= 2; // Multiple fields connecting = important
          
          // Use subtle styling for less important edges
            initialEdges.push({
            id: `${entity.name}-${field.foreign_key.table}-${field.name}`,
              source: field.foreign_key.table,
              target: entity.name,
            type: 'straight',
            animated: false,
              markerEnd: {
                type: 'arrowclosed',
              width: isImportant ? 20 : 15,
              height: isImportant ? 20 : 15,
              color: isImportant ? '#475569' : '#94a3b8',
            },
            style: { 
              stroke: isImportant ? '#475569' : '#94a3b8', 
              strokeWidth: isImportant ? 2 : 1,
              opacity: isImportant ? 0.8 : 0.3,
            },
            });
        }
      });
    });

    // Second pass: find tables sharing common entities and assign colors
    const groups = findCommonEntityGroups(schema.entities);
    
    const nodeColorMap: { [key: string]: { bg: string; border: string; text: string } } = {};
    groups.forEach((group, groupIndex) => {
      const color = colorPalette[groupIndex % colorPalette.length];
      group.forEach((tableName) => {
        nodeColorMap[tableName] = color;
      });
    });

    // Third pass: create hierarchical layout
    const levelBuckets = calculateHierarchicalLayout(schema.entities, initialEdges);
    
    const initialNodes: Node[] = [];
    let yOffset = 0;
    
    levelBuckets.forEach((level, levelIndex) => {
      const nodesInLevel = level.length;
      const spacingX = 400; // Horizontal spacing between nodes
      const baseX = -(nodesInLevel * spacingX) / 2 + spacingX / 2;
      
      level.forEach((tableName, indexInLevel) => {
        const entity = schema.entities.find((e: any) => e.name === tableName);
        if (!entity) return;
        
        const x = baseX + indexInLevel * spacingX;
        const y = yOffset;
        
        // Calculate dynamic height based on number of fields
        const fieldCount = (entity.fields || []).length;
        const dynamicHeight = Math.max(200, 120 + fieldCount * 32); // Base height + field height
        
        initialNodes.push({
          id: entity.name,
          type: 'tableNode',
          position: { x, y },
          data: {
            tableName: entity.name,
            fields: entity.fields || [],
            color: nodeColorMap[entity.name],
            onSizeChange: handleNodeSizeChange,
            onConnect: handleConnect,
            onFieldsChange: handleFieldsChange,
            currentNodeId: entity.name,
            allTables: initialNodes.map(n => ({ id: n.id, name: (n.data as TableNodeData).tableName || n.id })),
          },
          draggable: true,
          selectable: true,
          width: 300,
          height: dynamicHeight,
        });
      });
      
      yOffset += 500; // Vertical spacing between levels
    });

    // Preserve existing node positions if nodes already exist
    setNodes((existingNodes) => {
      if (existingNodes.length === 0) {
        // First time loading - use the initial layout
        return initialNodes;
      }
      
      // Update existing nodes with new data but preserve positions
      const updatedNodes = existingNodes.map(node => {
        const schemaEntity = schema.entities.find((e: any) => e.name === node.id);
        if (!schemaEntity) return node;
        
        // Find or create the node
        const newData = {
          tableName: schemaEntity.name,
          fields: schemaEntity.fields || [],
          color: nodeColorMap[schemaEntity.name] || node.data.color,
          onSizeChange: handleNodeSizeChange,
          onConnect: handleConnect,
          onFieldsChange: handleFieldsChange,
          currentNodeId: schemaEntity.name,
          allTables: initialNodes.map(n => ({ id: n.id, name: (n.data as TableNodeData).tableName || n.id })),
        };
        
        return {
          ...node,
          data: newData,
          // Keep existing position, width, height
        };
      });
      
      // Add any new nodes that don't exist yet
      const existingNodeIds = new Set(existingNodes.map(n => n.id));
      const newNodes = initialNodes.filter(node => !existingNodeIds.has(node.id));
      
      return [...updatedNodes, ...newNodes];
    });
    
    // Only update edges if they've changed
    setEdges((existingEdges) => {
      if (existingEdges.length === 0) {
        return initialEdges;
      }
      
      // For now, preserve existing edges unless they conflict
      // You might want to merge/reconcile edges here
      return existingEdges;
    });
  }, [schema, handleNodeSizeChange, handleConnect, handleFieldsChange]);

  // Auto-fetch suggestions when toggle is ON and schema updates
  useEffect(() => {
    if (aiSuggestionsEnabled && schema?.entities && schema.entities.length > 0) {
      setIsLoadingSuggestions(true);
      // Clear cache when fetching new suggestions for a new schema
      setCachedNodes({ option1: null, option2: null });
      setCachedEdges({ option1: null, option2: null });
      fetchAISuggestions(schema).then(suggestions => {
        setAiSuggestions(suggestions);
        setIsLoadingSuggestions(false);
      });
    }
  }, [schema, aiSuggestionsEnabled]);

  // Convert suggestions into nodes and edges for rendering - ONLY WHEN NOT LOADING - WITH CACHING
  useEffect(() => {
    // Don't update suggestions while still loading
    if (isLoadingSuggestions) {
      return;
    }
    
    // Check if we already have this cached
    if (activeSuggestionOption === 1 && cachedNodes.option1 && cachedEdges.option1) {
      console.log('Using cached Option 1');
      setSuggestionNodes(cachedNodes.option1);
      setSuggestionEdges(cachedEdges.option1);
      return;
    }
    
    if (activeSuggestionOption === 2 && cachedNodes.option2 && cachedEdges.option2) {
      console.log('Using cached Option 2');
      setSuggestionNodes(cachedNodes.option2);
      setSuggestionEdges(cachedEdges.option2);
      return;
    }
    
    console.log('Computing new suggestion nodes/edges for option:', activeSuggestionOption);
    
    if (!aiSuggestions) {
      console.log('No suggestions available');
      setSuggestionNodes([]);
      setSuggestionEdges([]);
      return;
    }
    
    if (activeSuggestionOption === 1) {
      // Option 1: Add new table
      const option1 = aiSuggestions?.option_1;
      console.log('Option 1 data:', option1);
      if (option1?.new_table) {
        const newTable = option1.new_table;
        
        // Find a smart position (top-right area) that doesn't overlap
        const existingNodes = nodes;
        const maxX = Math.max(...existingNodes.map(n => n.position.x), 0);
        const maxY = Math.max(...existingNodes.map(n => n.position.y), 0);
        
        // Calculate fixed size based on fields like regular tables
        const fieldCount = (newTable.fields || []).length;
        const fixedWidth = 300;
        const fixedHeight = Math.max(200, 120 + fieldCount * 32);
        
        const suggestionNode: Node = {
          id: `suggestion_${newTable.name}`,
          type: 'tableNode',
          position: { x: maxX + 450, y: 50 },
          data: {
            tableName: newTable.name,
            fields: newTable.fields || [],
            color: { bg: 'hsl(var(--card))', border: '#3b82f6', text: 'hsl(var(--foreground))' },
            isSuggestion: true,
            originalTable: newTable,
          },
          selectable: true,
          draggable: false,
          width: fixedWidth,
          height: fixedHeight,
          style: {
            opacity: 0.6,
            border: '2px dashed #3b82f6',
            boxShadow: '0 0 16px rgba(59, 130, 246, 0.4)',
            cursor: 'pointer',
            width: fixedWidth,
            height: fixedHeight,
          },
        };
        console.log('Created suggestion node:', suggestionNode);
        const suggestionNodeArray = [suggestionNode];
        setSuggestionNodes(suggestionNodeArray);
        setCachedNodes(prev => ({ ...prev, option1: suggestionNodeArray }));

        // Create edges for connections - point TO the existing table
        const newEdges: Edge[] = (option1.connections || []).map((conn: any, idx: number) => ({
          id: `suggestion_edge_${idx}`,
          source: `suggestion_${newTable.name}`,
          target: conn.to,
          type: 'straight' as const,
          animated: false,
          markerEnd: {
            type: 'arrowclosed' as const,
            width: 20,
            height: 20,
            color: '#3b82f6',
          },
          style: {
            stroke: '#3b82f6',
            strokeWidth: 2,
            opacity: 0.5,
            strokeDasharray: '8,4',
          },
        }));
        setSuggestionEdges(newEdges);
        setCachedEdges(prev => ({ ...prev, option1: newEdges }));
      }
    } else if (activeSuggestionOption === 2) {
      // Option 2: Merge tables
      const option2 = aiSuggestions?.option_2;
      if (option2?.merged_table) {
        const mergedTable = option2.merged_table;
        
        // Position the merged table in a smart location (lower right)
        const existingNodes = nodes;
        const maxX = Math.max(...existingNodes.map(n => n.position.x), 0);
        const maxY = Math.max(...existingNodes.map(n => n.position.y), 0);
        
        // Calculate fixed size based on fields like regular tables
        const fieldCount = (mergedTable.fields || []).length;
        const fixedWidth = 300;
        const fixedHeight = Math.max(200, 120 + fieldCount * 32);
        
        const suggestionNode: Node = {
          id: `suggestion_${mergedTable.name}`,
          type: 'tableNode',
          position: { x: maxX + 450, y: 350 },
          data: {
            tableName: mergedTable.name,
            fields: mergedTable.fields || [],
            color: { bg: 'hsl(var(--card))', border: '#10b981', text: 'hsl(var(--foreground))' },
            isSuggestion: true,
            originalTable: mergedTable,
          },
          selectable: true,
          draggable: false,
          width: fixedWidth,
          height: fixedHeight,
          style: {
            opacity: 0.6,
            border: '2px dashed #10b981',
            boxShadow: '0 0 16px rgba(16, 185, 129, 0.4)',
            cursor: 'pointer',
            width: fixedWidth,
            height: fixedHeight,
          },
        };
        const suggestionNodeArray = [suggestionNode];
        setSuggestionNodes(suggestionNodeArray);
        setCachedNodes(prev => ({ ...prev, option2: suggestionNodeArray }));

        // Create edges for connections - point TO other tables
        const newEdges: Edge[] = (option2.connections || []).map((conn: any, idx: number) => ({
          id: `suggestion_edge_${idx}`,
          source: `suggestion_${mergedTable.name}`,
          target: conn.to,
          type: 'straight' as const,
          animated: false,
          markerEnd: {
            type: 'arrowclosed' as const,
            width: 20,
            height: 20,
            color: '#10b981',
          },
          style: {
            stroke: '#10b981',
            strokeWidth: 2,
            opacity: 0.5,
            strokeDasharray: '8,4',
          },
        }));
        setSuggestionEdges(newEdges);
        setCachedEdges(prev => ({ ...prev, option2: newEdges }));
      }
    }
  }, [aiSuggestions, activeSuggestionOption, isLoadingSuggestions]);

  // Convert a ghost node into a regular table node
  const convertGhostToRealTable = useCallback((ghostNode: Node): Node => {
    const nodeData = ghostNode.data as TableNodeData & { isSuggestion?: boolean; originalTable?: any };
    const tableName = nodeData.originalTable?.name || nodeData.tableName || ghostNode.id;
    
    // Get a color for the new table
    const color = colorPalette[nodes.length % colorPalette.length];
    
    const realNode: Node = {
      id: tableName,
      type: 'tableNode',
      position: ghostNode.position, // Keep the same position
      data: {
        tableName: tableName,
        fields: nodeData.originalTable?.fields || nodeData.fields || [],
        color: color,
        onSizeChange: handleNodeSizeChange,
        onConnect: handleConnect,
        onFieldsChange: handleFieldsChange,
        currentNodeId: tableName,
      },
      draggable: true,
      selectable: true,
      width: ghostNode.width || 300,
      height: ghostNode.height || 200,
    };
    
    return realNode;
  }, [nodes, handleNodeSizeChange, handleConnect, handleFieldsChange]);

  // Handle clicking on a suggestion node to accept it
  const onNodeClick = useCallback((event: React.MouseEvent, node: Node) => {
    const nodeData = node.data as TableNodeData & { isSuggestion?: boolean; originalTable?: any };
    
    // Check if this is a suggestion node
    if (nodeData.isSuggestion && nodeData.originalTable) {
      console.log('Accepting suggestion node:', node.id);
      
      // Convert ghost to real table
      const realNode = convertGhostToRealTable(node);
      
      // Add the real node to the main nodes array
      setNodes((prevNodes) => {
        const allNodes = [...prevNodes, realNode];
        // Update allTables for all nodes including the new one
        return allNodes.map(node => ({
          ...node,
          data: {
            ...node.data,
            allTables: allNodes.map(n => ({ id: n.id, name: (n.data as TableNodeData).tableName || n.id })),
          },
        }));
      });
      
      // Convert suggestion edges to real edges
      setEdges((prevEdges) => {
        if (suggestionEdges.length > 0) {
          const realEdges = suggestionEdges
            .filter(edge => edge.source === node.id)
            .map(edge => ({
              ...edge,
              id: `${realNode.id}-${edge.target}`,
              source: realNode.id,
              style: {
                ...edge.style,
                opacity: 1,
                strokeDasharray: '0',
              },
            }));
          
          return [...prevEdges, ...realEdges];
        }
        return prevEdges;
      });
      
      // Remove the suggestion from the ghosts
      setSuggestionNodes([]);
      setSuggestionEdges([]);
    }
  }, [suggestionEdges, convertGhostToRealTable]);

  const onNodesChange = useCallback((changes: any) => {
    setNodes((nds) => {
      const updated = [...nds];
      changes.forEach((change: any) => {
        const index = updated.findIndex((n) => n.id === change.id);
        if (index !== -1) {
      if (change.type === 'position' && change.position) {
            updated[index] = { ...updated[index], position: change.position };
          } else if (change.type === 'resize' && change.dimensions) {
            // Handle NodeResizer resize events
            updated[index] = {
              ...updated[index],
              width: change.dimensions.width,
              height: change.dimensions.height,
            };
          } else if (change.type === 'select') {
            // Handle node selection
            updated[index] = { ...updated[index], selected: change.selected };
          }
        }
      });
      return updated;
    });
  }, []);

  const onEdgesChange = useCallback((changes: any) => {
    setEdges((eds) => changes.reduce((acc: Edge[], change: any) => {
      if (change.type === 'dimensions') {
        return acc.map((edge) =>
          edge.id === change.id ? { ...edge, ...change.dimensions } : edge
        );
      }
      if (change.type === 'remove') {
        return acc.filter((edge) => edge.id !== change.id);
      }
      return acc;
    }, eds));
  }, []);

  // Handle new connections (arrows between tables)
  const onConnect = useCallback((params: Connection) => {
    console.log('Connection attempted:', params);
    const edgeId = `${params.source}-${params.target}-${Date.now()}`;
    
    const newEdge = {
      ...params,
      id: edgeId,
      type: 'straight' as const,
      animated: false,
      markerEnd: {
        type: 'arrowclosed' as const,
        width: 20,
        height: 20,
        color: '#475569',
      },
      style: { 
        stroke: '#475569', 
        strokeWidth: 2,
        opacity: 0.8,
      },
    };
    
    setEdges((eds) => [...eds, newEdge]);
  }, []);

  // Handle updating schema from current visualization state
  const handleUpdateSchema = useCallback(() => {
    try {
      if (!onSchemaUpdate) return;
      
      console.log('handleUpdateSchema: Starting schema update');
      console.log('Current nodes:', nodes);
      console.log('Current edges:', edges);
      
      // Filter out any ghost/suggestion nodes (shouldn't be in main nodes, but just in case)
      const realNodes = nodes.filter(node => {
        const nodeData = node.data as TableNodeData & { isSuggestion?: boolean };
        return !nodeData.isSuggestion;
      });
      
      console.log('Real nodes after filtering:', realNodes);
      
      // Convert nodes back to entities
      const updatedEntities = realNodes.map(node => {
        let fields = (node.data as TableNodeData).fields || [];
        
        // If table has no fields, add a default id field for DynamoDB
        if (fields.length === 0) {
          fields = [
            {
              name: 'id',
              type: 'uuid',
              primary_key: true,
              required: true,
            }
          ];
        }
        // If table has fields but no primary key, add one to the first field
        else if (!fields.some((f: any) => f.primary_key)) {
          fields = fields.map((field: any, idx: number) => 
            idx === 0 ? { ...field, primary_key: true } : field
          );
        }
        
        return {
          name: (node.data as TableNodeData).tableName || node.id,
          fields: fields,
        };
             });
      
      // Create a map of target entities to their source entities (from edges)
      const targetToSourceMap = new Map<string, string>();
      edges.forEach(edge => {
        if (edge.target && edge.source) {
          targetToSourceMap.set(edge.target as string, edge.source as string);
        }
      });
      
      // Add foreign keys only to fields that don't already have one, and only for user-created edges
      updatedEntities.forEach(entity => {
        const hasForeignKey = entity.fields.some((f: any) => f.foreign_key);
        const sourceTable = targetToSourceMap.get(entity.name);
        
        if (sourceTable && !hasForeignKey) {
          // Add foreign key to the first suitable field (or create one)
          let fkAdded = false;
          entity.fields = entity.fields.map((field: any) => {
            // Only add FK if this field doesn't already have one
            if (!field.foreign_key && !fkAdded) {
              fkAdded = true;
              return {
                ...field,
                foreign_key: {
                  table: sourceTable,
                  column: 'id',
                },
              };
            }
            return field;
          });
          
          // If no field got the FK added, add a new field
          if (!fkAdded && entity.fields.length > 0) {
            const firstField = entity.fields[0];
            entity.fields[0] = {
              ...firstField,
              foreign_key: {
                table: sourceTable,
                column: 'id',
              },
            };
          }
        }
      });
      
      const updatedSchema = {
        ...schema,
        entities: updatedEntities,
      };
      
      console.log('Updated schema:', updatedSchema);
      onSchemaUpdate(updatedSchema);
    } catch (error) {
      console.error('Error in handleUpdateSchema:', error);
      alert(`Error updating schema: ${error}`);
    }
  }, [nodes, edges, schema, onSchemaUpdate]);

  // Handle adding new tables
  const addNewTable = useCallback(() => {
    const newTableName = `Table_${nodes.length + 1}`;
    const color = colorPalette[nodes.length % colorPalette.length];
    
    const newNode: Node = {
      id: newTableName,
      type: 'tableNode',
      position: { x: 100, y: 100 },
      data: {
        tableName: newTableName,
        fields: [],
        color: color,
        onSizeChange: handleNodeSizeChange,
        onConnect: handleConnect,
        onFieldsChange: handleFieldsChange,
        currentNodeId: newTableName,
      },
      draggable: true,
      selectable: true,
      width: 300,
      height: 200,
    };
    
    setNodes((nds) => {
      const allNodes = [...nds, newNode];
      // Update allTables for all nodes including the new one
      return allNodes.map(node => ({
        ...node,
        data: {
          ...node.data,
          allTables: allNodes.map(n => ({ id: n.id, name: (n.data as TableNodeData).tableName || n.id })),
        },
      }));
    });
  }, [nodes, handleNodeSizeChange, handleConnect, handleFieldsChange]);

  return (
    <div className="h-full w-full relative overflow-hidden" style={{ minWidth: 0 }}>
      <style>
        {`.react-flow__attribution { display: none !important; }`}
      </style>
      {/* Add Table Button */}
      <button
        onClick={addNewTable}
        className="absolute top-4 right-4 z-50 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-lg transition-colors flex items-center gap-2"
      >
        <Plus className="h-4 w-4" />
        Add Table
      </button>
      
      {/* AI Suggestions Toggle */}
      <button
        onClick={() => setAiSuggestionsEnabled(!aiSuggestionsEnabled)}
        className={`absolute top-20 right-4 z-50 px-4 py-2 rounded-lg shadow-lg transition-all flex items-center gap-2 ${
          aiSuggestionsEnabled
            ? 'bg-blue-700 hover:bg-blue-800 text-white'
            : 'bg-blue-600 hover:bg-blue-700 text-white'
        }`}
      >
        <Sparkles className="h-4 w-4" />
        AI Suggestions {aiSuggestionsEnabled ? 'ON' : 'OFF'}
      </button>

      {/* Option 1/2 Toggle Widget - Only show when AI suggestions are enabled and loaded */}
      {aiSuggestionsEnabled && aiSuggestions && (
        <div className="absolute top-36 right-4 z-50 bg-white rounded-lg shadow-lg border border-gray-200 p-2 flex items-center gap-2">
          <button
            onClick={() => setActiveSuggestionOption(1)}
            className={`px-3 py-1 rounded text-sm font-medium transition-all ${
              activeSuggestionOption === 1
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            ← Option 1
          </button>
          <div className="h-6 w-px bg-gray-300" />
          <button
            onClick={() => setActiveSuggestionOption(2)}
            className={`px-3 py-1 rounded text-sm font-medium transition-all ${
              activeSuggestionOption === 2
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            Option 2 →
          </button>
        </div>
      )}

      {/* Loading indicator */}
      {isLoadingSuggestions && (
        <div className="absolute top-36 right-4 z-50 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg">
          Generating suggestions...
        </div>
      )}
      
      {/* Update Schema Button */}
      {onSchemaUpdate && (
        <button
          onClick={handleUpdateSchema}
          className="absolute top-4 left-4 z-50 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg shadow-lg transition-colors flex items-center gap-2"
        >
          Update Schema
        </button>
      )}
      
      <ReactFlow
        nodes={(() => {
          // Only show suggestions if loading is complete
          const shouldShowSuggestions = aiSuggestionsEnabled && aiSuggestions && !isLoadingSuggestions;
          const finalNodes = shouldShowSuggestions ? [...nodes, ...suggestionNodes] : nodes;
          console.log('Rendering ReactFlow with nodes:', { 
            nodeCount: finalNodes.length, 
            suggestionNodeCount: suggestionNodes.length,
            aiSuggestionsEnabled,
            hasSuggestions: !!aiSuggestions,
            isLoadingSuggestions
          });
          return finalNodes;
        })()}
        edges={(() => {
          const shouldShowSuggestions = aiSuggestionsEnabled && aiSuggestions && !isLoadingSuggestions;
          return shouldShowSuggestions ? [...edges, ...suggestionEdges] : edges;
        })()}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        onNodeClick={onNodeClick}
        nodeTypes={nodeTypes}
        fitView
        className="bg-background"
        minZoom={0.05}
        maxZoom={2}
        nodesDraggable={true}
        nodesConnectable={true}
        elementsSelectable={true}
        panOnScroll={false}
        connectionLineStyle={{ stroke: '#94a3b8', strokeWidth: 2 }}
        defaultEdgeOptions={{
          style: { strokeWidth: 1.5 },
          animated: false,
          type: 'straight',
        }}
        proOptions={{ hideAttribution: true }}
      >
        <Background variant={BackgroundVariant.Dots} gap={25} size={1} />
        <Controls className="bg-card border border-border rounded-lg shadow-lg [&_button]:bg-blue-600 [&_button:hover]:bg-blue-700 [&_button]:text-white [&_button_svg]:text-white" />
      </ReactFlow>
    </div>
  );
};
