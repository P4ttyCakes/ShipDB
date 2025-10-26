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
  addEdge,
  useNodesState,
  useEdgesState,
  NodeResizer,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import { Trash2, Plus } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';

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

  const handleAddField = () => {
    const newField = { name: `field_${fields.length + 1}`, type: 'text', primaryKey: false, required: false };
    setFields([...fields, newField]);
    setEditingField(fields.length);
  };

  const handleRemoveField = (index: number) => {
    setFields(fields.filter((_: any, i: number) => i !== index));
  };

  const handleUpdateField = (index: number, updates: any) => {
    setFields(fields.map((field: any, i: number) => (i === index ? { ...field, ...updates } : field)));
  };

  const bgColor = data?.color?.bg || 'hsl(var(--card))';
  const borderColor = data?.color?.border || 'hsl(var(--border))';
  const textColor = data?.color?.text || 'hsl(var(--foreground))';
  
  const width = props.width || 300;
  const height = props.height || 400;

  // Handle resize - call parent's onSizeChange callback
  const handleResizeStart = (e: React.MouseEvent) => {
    e.stopPropagation();
    const startX = e.clientX;
    const startY = e.clientY;
    const startWidth = width;
    const startHeight = height;

    const handleMouseMove = (e: MouseEvent) => {
      const deltaX = e.clientX - startX;
      const deltaY = e.clientY - startY;
      
      let newWidth = startWidth + deltaX;
      let newHeight = startHeight + deltaY;
      
      newWidth = Math.max(250, newWidth);
      newHeight = Math.max(200, newHeight);
      
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
  };

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
      {/* Resize Handle - Bottom Right Corner */}
      <div
        className="absolute -bottom-1 -right-1 w-4 h-4 cursor-nwse-resize z-10 hover:scale-110 transition-transform"
        style={{
          backgroundColor: borderColor,
          border: '3px solid white',
          borderRadius: '2px',
        }}
        onMouseDown={handleResizeStart}
      />
      
      <Handle type="source" position={Position.Right} id="right" />
      <Handle type="target" position={Position.Left} id="left" />
      <Handle type="source" position={Position.Bottom} id="bottom" />
      <Handle type="target" position={Position.Top} id="top" />
      
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
      
      {/* Fields */}
      <div className="p-2 space-y-1 h-[calc(100%-4rem)] overflow-y-auto">
        {fields.map((field: any, idx: number) => (
          <div 
            key={idx} 
            className={`flex items-center gap-2 text-xs py-1 px-2 rounded hover:bg-black/5 transition-colors ${
              editingField === idx ? 'bg-primary/10' : ''
            }`}
          >
            {editingField === idx ? (
              <>
                <Input
                  value={field.name}
                  onChange={(e) => handleUpdateField(idx, { name: e.target.value })}
                  placeholder="Field name"
                  className="flex-1 h-7 text-xs"
                  autoFocus
                  onBlur={() => setEditingField(null)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === 'Escape') setEditingField(null);
                  }}
                />
                <Input
                  value={field.type}
                  onChange={(e) => handleUpdateField(idx, { type: e.target.value })}
                  placeholder="Type"
                  className="w-20 h-7 text-xs"
                  onBlur={() => setEditingField(null)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === 'Escape') setEditingField(null);
                  }}
                />
              </>
            ) : (
              <>
                <span 
                  className={`font-mono flex-1 cursor-pointer hover:opacity-80 transition-opacity ${field.primaryKey ? 'font-bold' : ''}`}
                  onClick={() => setEditingField(idx)}
                  style={{ color: field.primaryKey ? 'hsl(var(--primary))' : 'hsl(var(--foreground))' }}
                >
                  {field.name}
                </span>
                <span className="text-xs bg-muted px-2 py-0.5 rounded" style={{ color: 'hsl(var(--muted-foreground))' }}>{field.type}</span>
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
        ))}
        <Button
          size="sm"
          variant="outline"
          onClick={handleAddField}
          className="w-full h-7 text-xs mt-2"
        >
          <Plus className="mr-2 h-3 w-3" />
          Add Field
        </Button>
      </div>
    </div>
  );
};

const nodeTypes: NodeTypes = {
  tableNode: TableNode,
};

// Helper function to find tables that share common entities
// Color-code tables that share fields/entities (e.g., both have product_id, user_id, etc.)
const findCommonEntityGroups = (entities: any[]) => {
  // Build a map of entity names that appear in multiple tables
  const entityReferences: { [key: string]: Set<string> } = {};
  
  entities.forEach((entity) => {
    entity.fields?.forEach((field: any) => {
      // Check if this field references another table
      if (field.foreign_key?.table) {
        const refTable = field.foreign_key.table;
        if (!entityReferences[refTable]) {
          entityReferences[refTable] = new Set();
        }
        entityReferences[refTable].add(entity.name);
      }
    });
  });
  
  // Find entities that appear in multiple tables
  const sharedEntities = Object.entries(entityReferences)
    .filter(([_, tables]) => tables.size > 1)
    .map(([entityName]) => entityName);
  
  if (sharedEntities.length === 0) {
    return [];
  }
  
  // Build groups: tables that share the same referenced entity
  const groups: string[][] = [];
  const processed = new Set<string>();
  
  sharedEntities.forEach((sharedEntity) => {
    const tablesWithEntity = Array.from(entityReferences[sharedEntity]);
    
    // Only create groups if multiple tables reference this entity
    if (tablesWithEntity.length > 1) {
      const key = [...tablesWithEntity].sort().join('-');
      if (!processed.has(key)) {
        processed.add(key);
        groups.push(tablesWithEntity);
      }
    }
  });
  
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

export const InteractiveSchemaVisualization = ({ schema }: InteractiveSchemaVisualizationProps) => {
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

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
            label: field.name,
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
              opacity: isImportant ? 0.8 : 0.3, // Much more subtle for less important
            },
            labelStyle: { 
              fill: isImportant ? '#334155' : '#64748b', 
              fontSize: isImportant ? 11 : 9, 
              fontWeight: isImportant ? 600 : 400
            },
            labelBgStyle: { 
              fill: '#ffffff', 
              fillOpacity: 0.95,
              padding: '2px 4px',
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
        
        initialNodes.push({
          id: entity.name,
          type: 'tableNode',
          position: { x, y },
          data: {
            tableName: entity.name,
            fields: entity.fields || [],
            color: nodeColorMap[entity.name],
            onSizeChange: handleNodeSizeChange,
          },
          draggable: true,
          selectable: true,
          width: 300,
          height: 400,
        });
      });
      
      yOffset += 500; // Vertical spacing between levels
    });

    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [schema, handleNodeSizeChange]);

  const onNodesChange = useCallback((changes: any) => {
    setNodes((nds) => {
      const updated = [...nds];
      changes.forEach((change: any) => {
        const index = updated.findIndex((n) => n.id === change.id);
        if (index !== -1) {
          if (change.type === 'position' && change.position) {
            updated[index] = { ...updated[index], position: change.position };
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
      return acc;
    }, eds));
  }, []);

  return (
    <div className="h-full w-full relative">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        fitView
        className="bg-background"
        minZoom={0.05}
        maxZoom={2}
        nodesDraggable={true}
        nodesConnectable={false}
        elementsSelectable={true}
        connectionLineStyle={{ stroke: '#94a3b8', strokeWidth: 1 }}
        defaultEdgeOptions={{
          style: { strokeWidth: 1.5 },
          animated: false,
          type: 'straight',
        }}
      >
        <Background variant={BackgroundVariant.Dots} gap={25} size={1} />
        <Controls className="bg-card border border-border rounded-lg shadow-lg" />
      </ReactFlow>

      <div className="absolute bottom-4 left-4 bg-card border border-border rounded-lg p-3 shadow-lg z-10 max-w-sm">
        <p className="text-xs text-muted-foreground">
          💡 <strong>Click</strong> table/field names to edit • <strong>Drag</strong> to rearrange • <strong>Resize</strong> corners • <strong>Delete</strong> fields with trash icon
        </p>
        <p className="text-xs text-muted-foreground mt-2">
          Colored borders indicate tables that share common entities • Bold arrows show important relationships
        </p>
      </div>
    </div>
  );
};
