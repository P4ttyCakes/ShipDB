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
import { Trash2, Plus, Sparkles, X, Loader2, Link2, Settings2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { Textarea } from '@/components/ui/textarea';

interface Field {
  name: string;
  type: string;
  primaryKey?: boolean;
  primary_key?: boolean;
  foreignKey?: any;
  foreign_key?: {
    table: string;
    field: string;
    onDelete?: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION';
    onUpdate?: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION';
  };
  required?: boolean;
  unique?: boolean;
  default?: string | number;
  autoIncrement?: boolean;
  auto_increment?: boolean;
  length?: number;
  precision?: number;
  scale?: number;
  min?: number | string;
  max?: number | string;
  minLength?: number;
  maxLength?: number;
  enum?: string[];
  check?: string;
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
  onReject?: (nodeId: string) => void;
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
  const [fkDialogOpen, setFkDialogOpen] = useState(false);
  const [fkEditingIndex, setFkEditingIndex] = useState<number | null>(null);
  const [fkFormData, setFkFormData] = useState<{
    targetTable: string;
    targetField: string;
    onDelete: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION';
    onUpdate: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION';
  }>({
    targetTable: '',
    targetField: 'id',
    onDelete: 'RESTRICT',
    onUpdate: 'RESTRICT',
  });
  const [fieldPropsDialogOpen, setFieldPropsDialogOpen] = useState(false);
  const [fieldPropsEditingIndex, setFieldPropsEditingIndex] = useState<number | null>(null);
  const [fieldPropsFormData, setFieldPropsFormData] = useState<{
    unique: boolean;
    required: boolean;
    default: string;
    autoIncrement: boolean;
    length: string;
    precision: string;
    scale: string;
    min: string;
    max: string;
    minLength: string;
    maxLength: string;
    enum: string[];
    check: string;
  }>({
    unique: false,
    required: true,
    default: '',
    autoIncrement: false,
    length: '',
    precision: '',
    scale: '',
    min: '',
    max: '',
    minLength: '',
    maxLength: '',
    enum: [],
    check: '',
  });

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

  const handleOpenFkDialog = (index: number) => {
    const field = fields[index];
    const existingFk = field.foreign_key || field.foreignKey;
    
    setFkEditingIndex(index);
    setFkFormData({
      targetTable: existingFk?.table || '',
      targetField: existingFk?.field || 'id',
      onDelete: existingFk?.onDelete || 'RESTRICT',
      onUpdate: existingFk?.onUpdate || 'RESTRICT',
    });
    setFkDialogOpen(true);
  };

  const handleSaveFk = () => {
    if (fkEditingIndex !== null && fkFormData.targetTable) {
      handleUpdateField(fkEditingIndex, {
        foreign_key: {
          table: fkFormData.targetTable,
          field: fkFormData.targetField,
          onDelete: fkFormData.onDelete,
          onUpdate: fkFormData.onUpdate,
        },
      });
      setFkDialogOpen(false);
      setFkEditingIndex(null);
    }
  };

  const handleRemoveFk = () => {
    if (fkEditingIndex !== null) {
      handleUpdateField(fkEditingIndex, {
        foreign_key: undefined,
        foreignKey: undefined,
      });
      setFkDialogOpen(false);
      setFkEditingIndex(null);
    }
  };

  const handleTogglePrimaryKey = (index: number) => {
    const field = fields[index];
    const isCurrentlyPk = field.primaryKey || field.primary_key;
    
    // Toggle primary key
    handleUpdateField(index, {
      primaryKey: !isCurrentlyPk,
      primary_key: !isCurrentlyPk,
    });
  };

  const handleOpenFieldPropsDialog = (index: number) => {
    const field = fields[index];
    
    setFieldPropsEditingIndex(index);
    setFieldPropsFormData({
      unique: field.unique || false,
      required: field.required !== undefined ? field.required : true,
      default: field.default !== undefined ? String(field.default) : '',
      autoIncrement: field.autoIncrement || field.auto_increment || false,
      length: field.length !== undefined ? String(field.length) : '',
      precision: field.precision !== undefined ? String(field.precision) : '',
      scale: field.scale !== undefined ? String(field.scale) : '',
      min: field.min !== undefined ? String(field.min) : '',
      max: field.max !== undefined ? String(field.max) : '',
      minLength: field.minLength !== undefined ? String(field.minLength) : '',
      maxLength: field.maxLength !== undefined ? String(field.maxLength) : '',
      enum: field.enum || [],
      check: field.check || '',
    });
    setFieldPropsDialogOpen(true);
  };

  const handleSaveFieldProps = () => {
    if (fieldPropsEditingIndex !== null) {
      const updates: any = {
        unique: fieldPropsFormData.unique,
        required: fieldPropsFormData.required,
        autoIncrement: fieldPropsFormData.autoIncrement,
        auto_increment: fieldPropsFormData.autoIncrement,
      };

      // Only add properties if they have values, otherwise clear them
      if (fieldPropsFormData.default.trim()) {
        // Try to parse as number, otherwise keep as string
        const numValue = Number(fieldPropsFormData.default);
        updates.default = isNaN(numValue) ? fieldPropsFormData.default : numValue;
      } else {
        updates.default = undefined;
      }

      if (fieldPropsFormData.length.trim()) {
        updates.length = parseInt(fieldPropsFormData.length) || undefined;
      } else {
        updates.length = undefined;
      }
      if (fieldPropsFormData.precision.trim()) {
        updates.precision = parseInt(fieldPropsFormData.precision) || undefined;
      } else {
        updates.precision = undefined;
      }
      if (fieldPropsFormData.scale.trim()) {
        updates.scale = parseInt(fieldPropsFormData.scale) || undefined;
      } else {
        updates.scale = undefined;
      }
      if (fieldPropsFormData.min.trim()) {
        const numValue = Number(fieldPropsFormData.min);
        updates.min = isNaN(numValue) ? fieldPropsFormData.min : numValue;
      } else {
        updates.min = undefined;
      }
      if (fieldPropsFormData.max.trim()) {
        const numValue = Number(fieldPropsFormData.max);
        updates.max = isNaN(numValue) ? fieldPropsFormData.max : numValue;
      } else {
        updates.max = undefined;
      }
      if (fieldPropsFormData.minLength.trim()) {
        updates.minLength = parseInt(fieldPropsFormData.minLength) || undefined;
      } else {
        updates.minLength = undefined;
      }
      if (fieldPropsFormData.maxLength.trim()) {
        updates.maxLength = parseInt(fieldPropsFormData.maxLength) || undefined;
      } else {
        updates.maxLength = undefined;
      }
      if (fieldPropsFormData.enum.length > 0) {
        updates.enum = fieldPropsFormData.enum;
      } else {
        updates.enum = undefined;
      }
      if (fieldPropsFormData.check.trim()) {
        updates.check = fieldPropsFormData.check;
      } else {
        updates.check = undefined;
      }

      handleUpdateField(fieldPropsEditingIndex, updates);
      setFieldPropsDialogOpen(false);
      setFieldPropsEditingIndex(null);
    }
  };

  // Get available tables for FK target (exclude current table)
  const availableTables = (data?.allTables || []).filter(
    (table: { id: string; name: string }) => table.id !== props.id
  );

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
      {/* Reject Button - Top Right - Only for suggestions */}
      {isSuggestion && data?.onReject && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            if (data.onReject) {
              data.onReject(props.id as string);
            }
          }}
          className="absolute top-2 right-2 z-50 bg-red-500 hover:bg-red-600 text-white rounded-full p-1.5 shadow-lg transition-colors flex items-center justify-center"
          style={{ width: '24px', height: '24px' }}
        >
          <X className="h-3 w-3" />
        </button>
      )}
      
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
                {(field.primaryKey || field.primary_key) && (
                  <span 
                    className="text-xs bg-blue-500/20 text-blue-600 px-2 py-0.5 rounded cursor-pointer hover:bg-blue-500/30 transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTogglePrimaryKey(idx);
                    }}
                    title="Click to remove primary key"
                  >
                    PK
                  </span>
                )}
                {!(field.primaryKey || field.primary_key) && (
                  <span 
                    className="text-xs bg-gray-200/50 text-gray-500 px-2 py-0.5 rounded cursor-pointer hover:bg-blue-500/20 hover:text-blue-600 transition-colors"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleTogglePrimaryKey(idx);
                    }}
                    title="Click to set as primary key"
                  >
                    PK
                  </span>
                )}
                {(field.foreign_key || field.foreignKey) && (
                  <span 
                    className="text-xs bg-green-500/20 text-green-600 px-2 py-0.5 rounded cursor-help"
                    title={`FK → ${(field.foreign_key || field.foreignKey)?.table || '?'}.${(field.foreign_key || field.foreignKey)?.field || 'id'}`}
                  >
                    FK
                  </span>
                )}
                {field.unique && (
                  <span className="text-xs bg-purple-500/20 text-purple-600 px-2 py-0.5 rounded" title="Unique constraint">UQ</span>
                )}
                {!field.required && (
                  <span className="text-xs bg-orange-500/20 text-orange-600 px-2 py-0.5 rounded">NULL</span>
                )}
              </>
            )}
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOpenFkDialog(idx);
                  }}
                  className="h-6 w-6 p-0 hover:bg-primary/10 hover:text-primary"
                  title="Set Foreign Key"
                >
                  <Link2 className="h-3 w-3" />
                </Button>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOpenFieldPropsDialog(idx);
                  }}
                  className="h-6 w-6 p-0 hover:bg-primary/10 hover:text-primary"
                  title="Field Properties"
                >
                  <Settings2 className="h-3 w-3" />
                </Button>
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

      {/* Foreign Key Dialog */}
      <Dialog open={fkDialogOpen} onOpenChange={setFkDialogOpen}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle>Set Foreign Key</DialogTitle>
            <DialogDescription>
              Configure the foreign key relationship for this field.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="target-table">Target Table</Label>
              <Select
                value={fkFormData.targetTable}
                onValueChange={(value) => setFkFormData({ ...fkFormData, targetTable: value })}
              >
                <SelectTrigger id="target-table">
                  <SelectValue placeholder="Select target table" />
                </SelectTrigger>
                <SelectContent>
                  {availableTables.length > 0 ? (
                    availableTables.map((table: { id: string; name: string }) => (
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

            <div className="grid gap-2">
              <Label htmlFor="target-field">Target Field</Label>
              <Input
                id="target-field"
                value={fkFormData.targetField}
                onChange={(e) => setFkFormData({ ...fkFormData, targetField: e.target.value })}
                placeholder="id"
              />
              <p className="text-xs text-muted-foreground">
                The field in the target table (defaults to "id")
              </p>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="on-delete">ON DELETE</Label>
              <Select
                value={fkFormData.onDelete}
                onValueChange={(value: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION') => 
                  setFkFormData({ ...fkFormData, onDelete: value })
                }
              >
                <SelectTrigger id="on-delete">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="CASCADE">CASCADE</SelectItem>
                  <SelectItem value="SET NULL">SET NULL</SelectItem>
                  <SelectItem value="RESTRICT">RESTRICT</SelectItem>
                  <SelectItem value="NO ACTION">NO ACTION</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="on-update">ON UPDATE</Label>
              <Select
                value={fkFormData.onUpdate}
                onValueChange={(value: 'CASCADE' | 'SET NULL' | 'RESTRICT' | 'NO ACTION') => 
                  setFkFormData({ ...fkFormData, onUpdate: value })
                }
              >
                <SelectTrigger id="on-update">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="CASCADE">CASCADE</SelectItem>
                  <SelectItem value="SET NULL">SET NULL</SelectItem>
                  <SelectItem value="RESTRICT">RESTRICT</SelectItem>
                  <SelectItem value="NO ACTION">NO ACTION</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <DialogFooter>
            {(fields[fkEditingIndex || 0]?.foreign_key || fields[fkEditingIndex || 0]?.foreignKey) && (
              <Button
                variant="destructive"
                onClick={handleRemoveFk}
              >
                Remove FK
              </Button>
            )}
            <Button
              variant="outline"
              onClick={() => {
                setFkDialogOpen(false);
                setFkEditingIndex(null);
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSaveFk}
              disabled={!fkFormData.targetTable}
            >
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Field Properties Dialog */}
      <Dialog open={fieldPropsDialogOpen} onOpenChange={setFieldPropsDialogOpen}>
        <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Field Properties</DialogTitle>
            <DialogDescription>
              Configure advanced properties for this field.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            {/* Basic Constraints */}
            <div className="grid gap-4">
              <h4 className="text-sm font-semibold">Constraints</h4>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="unique"
                  checked={fieldPropsFormData.unique}
                  onCheckedChange={(checked) => 
                    setFieldPropsFormData({ ...fieldPropsFormData, unique: checked as boolean })
                  }
                />
                <Label htmlFor="unique" className="cursor-pointer">Unique</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="required"
                  checked={fieldPropsFormData.required}
                  onCheckedChange={(checked) => 
                    setFieldPropsFormData({ ...fieldPropsFormData, required: checked as boolean })
                  }
                />
                <Label htmlFor="required" className="cursor-pointer">Required (NOT NULL)</Label>
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox
                  id="auto-increment"
                  checked={fieldPropsFormData.autoIncrement}
                  onCheckedChange={(checked) => 
                    setFieldPropsFormData({ ...fieldPropsFormData, autoIncrement: checked as boolean })
                  }
                />
                <Label htmlFor="auto-increment" className="cursor-pointer">Auto Increment</Label>
              </div>
            </div>

            {/* Default Value */}
            <div className="grid gap-2">
              <Label htmlFor="default-value">Default Value</Label>
              <Input
                id="default-value"
                value={fieldPropsFormData.default}
                onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, default: e.target.value })}
                placeholder="e.g., 0, 'text', NOW()"
              />
            </div>

            {/* Type-specific Properties */}
            <div className="grid gap-4">
              <h4 className="text-sm font-semibold">Type Properties</h4>
              
              {/* Length (for VARCHAR, CHAR, etc.) */}
              <div className="grid gap-2">
                <Label htmlFor="length">Length</Label>
                <Input
                  id="length"
                  type="number"
                  value={fieldPropsFormData.length}
                  onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, length: e.target.value })}
                  placeholder="e.g., 255 for VARCHAR(255)"
                />
              </div>

              {/* Precision and Scale (for DECIMAL, NUMERIC) */}
              <div className="grid grid-cols-2 gap-2">
                <div className="grid gap-2">
                  <Label htmlFor="precision">Precision</Label>
                  <Input
                    id="precision"
                    type="number"
                    value={fieldPropsFormData.precision}
                    onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, precision: e.target.value })}
                    placeholder="e.g., 10"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="scale">Scale</Label>
                  <Input
                    id="scale"
                    type="number"
                    value={fieldPropsFormData.scale}
                    onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, scale: e.target.value })}
                    placeholder="e.g., 2"
                  />
                </div>
              </div>
            </div>

            {/* Check Constraints */}
            <div className="grid gap-4">
              <h4 className="text-sm font-semibold">Check Constraints</h4>
              
              <div className="grid grid-cols-2 gap-2">
                <div className="grid gap-2">
                  <Label htmlFor="min-value">Min Value</Label>
                  <Input
                    id="min-value"
                    value={fieldPropsFormData.min}
                    onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, min: e.target.value })}
                    placeholder="Minimum value"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="max-value">Max Value</Label>
                  <Input
                    id="max-value"
                    value={fieldPropsFormData.max}
                    onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, max: e.target.value })}
                    placeholder="Maximum value"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="grid gap-2">
                  <Label htmlFor="min-length">Min Length</Label>
                  <Input
                    id="min-length"
                    type="number"
                    value={fieldPropsFormData.minLength}
                    onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, minLength: e.target.value })}
                    placeholder="Minimum length"
                  />
                </div>
                <div className="grid gap-2">
                  <Label htmlFor="max-length">Max Length</Label>
                  <Input
                    id="max-length"
                    type="number"
                    value={fieldPropsFormData.maxLength}
                    onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, maxLength: e.target.value })}
                    placeholder="Maximum length"
                  />
                </div>
              </div>

              <div className="grid gap-2">
                <Label htmlFor="check-constraint">Custom Check Constraint</Label>
                <Input
                  id="check-constraint"
                  value={fieldPropsFormData.check}
                  onChange={(e) => setFieldPropsFormData({ ...fieldPropsFormData, check: e.target.value })}
                  placeholder="e.g., value > 0 AND value < 100"
                />
              </div>
            </div>

            {/* Enum Values */}
            <div className="grid gap-4">
              <h4 className="text-sm font-semibold">Enum Values</h4>
              <div className="grid gap-2">
                <Label>Enum Options (one per line)</Label>
                <Textarea
                  value={fieldPropsFormData.enum.join('\n')}
                  onChange={(e) => {
                    const enumValues = e.target.value.split('\n').filter(v => v.trim());
                    setFieldPropsFormData({ ...fieldPropsFormData, enum: enumValues });
                  }}
                  placeholder="option1&#10;option2&#10;option3"
                  rows={4}
                />
                <p className="text-xs text-muted-foreground">
                  Enter one enum value per line. Leave empty if not using enum type.
                </p>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setFieldPropsDialogOpen(false);
                setFieldPropsEditingIndex(null);
              }}
            >
              Cancel
            </Button>
            <Button onClick={handleSaveFieldProps}>
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
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
const fetchAISuggestions = async (schemaData: any, rejectedSuggestions: string[] = [], previouslySuggested: string[] = []) => {
  try {
    const response = await fetch('http://localhost:8000/api/schema/suggestions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        schema: schemaData,
        rejected_suggestions: rejectedSuggestions,
        previously_suggested: previouslySuggested
      }),
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
  const [aiSuggestions, setAiSuggestions] = useState<any>(null);
  const [isLoadingSuggestions, setIsLoadingSuggestions] = useState(false);
  const [suggestionNodes, setSuggestionNodes] = useState<Node[]>([]);
  const [suggestionEdges, setSuggestionEdges] = useState<Edge[]>([]);
  const [cachedNodes, setCachedNodes] = useState<{ option1: Node[] | null, option2: Node[] | null }>({ option1: null, option2: null });
  const [cachedEdges, setCachedEdges] = useState<{ option1: Edge[] | null, option2: Edge[] | null }>({ option1: null, option2: null });
  const [rejectedSuggestions, setRejectedSuggestions] = useState<string[]>([]);
  const [previouslySuggested, setPreviouslySuggested] = useState<string[]>([]);

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
    try {
      if (!schema?.entities) {
        console.warn('Schema missing entities, skipping node creation');
        return;
      }
      
      if (!Array.isArray(schema.entities)) {
        console.error('Schema entities is not an array:', schema.entities);
        return;
      }
      
      console.log('Creating nodes from schema with', schema.entities.length, 'entities');

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
        console.log('First time loading, creating', initialNodes.length, 'nodes');
        return initialNodes;
      }
      
      console.log('Updating', existingNodes.length, 'existing nodes with', schema.entities.length, 'entities');
      
      // Update existing nodes with new data but preserve positions
      const updatedNodes = existingNodes.map(node => {
        const schemaEntity = schema.entities.find((e: any) => e.name === node.id);
        if (!schemaEntity) {
          // Node exists in visualization but not in schema - keep it (might be manually added)
          console.log('Keeping node not in schema:', node.id);
          return node;
        }
        
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
      
      console.log('Adding', newNodes.length, 'new nodes, keeping', updatedNodes.length, 'updated nodes');
      
      const finalNodes = [...updatedNodes, ...newNodes];
      
      // Ensure we have at least some nodes - if not, something went wrong
      if (finalNodes.length === 0 && schema.entities.length > 0) {
        console.error('No nodes created but schema has entities! Falling back to initial nodes');
        return initialNodes;
      }
      
      return finalNodes;
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
    } catch (error) {
      console.error('Error creating nodes from schema:', error);
      // Don't clear nodes on error - keep existing visualization
      // Just log the error
    }
  }, [schema, handleNodeSizeChange, handleConnect, handleFieldsChange]);

  // Handle fetching AI suggestions manually
  const handleFetchSuggestions = useCallback(async () => {
    if (!schema?.entities || schema.entities.length === 0) {
      return;
    }
    
    setIsLoadingSuggestions(true);
    // Clear previous suggestions and cache
    setSuggestionNodes([]);
    setSuggestionEdges([]);
    setCachedNodes({ option1: null, option2: null });
    setCachedEdges({ option1: null, option2: null });
    
    const suggestions = await fetchAISuggestions(schema, rejectedSuggestions, previouslySuggested);
    if (suggestions) {
      setAiSuggestions(suggestions);
      
      // Track which tables were suggested in this response
      const suggestedTableNames: string[] = [];
      if (suggestions.option_1?.new_table?.name) {
        suggestedTableNames.push(suggestions.option_1.new_table.name);
      }
      if (suggestions.option_2?.merged_table?.name) {
        suggestedTableNames.push(suggestions.option_2.merged_table.name);
      }
      
      // Add to previously suggested list (avoid duplicates)
      if (suggestedTableNames.length > 0) {
        setPreviouslySuggested(prev => {
          const normalizedNew = suggestedTableNames.map(n => n.toLowerCase().trim());
          const normalizedPrev = prev.map(p => p.toLowerCase().trim());
          const toAdd = suggestedTableNames.filter(name => 
            !normalizedPrev.includes(name.toLowerCase().trim())
          );
          return [...prev, ...toAdd];
        });
      }
    }
    setIsLoadingSuggestions(false);
  }, [schema, rejectedSuggestions, previouslySuggested]);
  
  // Handle rejecting a suggestion
  const handleRejectSuggestion = useCallback((nodeId: string) => {
    // Find the node in current state to extract table name
    setSuggestionNodes(prev => {
      const node = prev.find(n => n.id === nodeId);
      if (!node) return prev;
      
      const nodeData = node.data as TableNodeData & { originalTable?: any };
      const tableName = nodeData.originalTable?.name || nodeData.tableName || nodeId.replace('suggestion_', '');
      
      console.log('Rejecting suggestion:', tableName);
      
      // Schedule state updates after this setState completes
      setTimeout(() => {
        // Add to rejected suggestions list (normalize for consistency)
        const normalizedTableName = tableName.toLowerCase().trim();
        setRejectedSuggestions(rejected => {
          const normalizedRejected = rejected.map(r => r.toLowerCase().trim());
          if (!normalizedRejected.includes(normalizedTableName)) {
            console.log('Adding to rejected list:', tableName);
            return [...rejected, tableName];
          }
          console.log('Already in rejected list:', tableName);
          return rejected;
        });
        
        // Clear AI suggestions to prevent regeneration
        setAiSuggestions(null);
        
        // Clear cache (no longer needed since we only show one suggestion)
        setCachedNodes({ option1: null, option2: null });
        setCachedEdges({ option1: null, option2: null });
      }, 0);
      
      return prev.filter(n => n.id !== nodeId);
    });
    
    // Remove edges connected to this node
    setSuggestionEdges(prev => prev.filter(e => e.source !== nodeId && e.target !== nodeId));
  }, []);

  // Convert suggestions into nodes and edges for rendering - ONLY WHEN NOT LOADING
  // Show only ONE suggestion at a time (randomly pick between option 1 and 2)
  useEffect(() => {
    // Don't update suggestions while still loading
    if (isLoadingSuggestions) {
      return;
    }
    
    if (!aiSuggestions) {
      console.log('No suggestions available');
      setSuggestionNodes([]);
      setSuggestionEdges([]);
      return;
    }
    
    // Filter out rejected suggestions and pick between option 1 and option 2
    let selectedOption = null;
    let isOption1 = false;
    
    // Normalize table names for comparison (lowercase, trim)
    const normalizeTableName = (name: string) => name.toLowerCase().trim();
    
    // Only filter out explicitly rejected tables on the frontend
    // The backend handles previously suggested uniqueness
    const normalizedRejected = rejectedSuggestions.map(normalizeTableName);
    
    console.log('Checking suggestions:', {
      rejectedSuggestions,
      previouslySuggested,
      option1: aiSuggestions?.option_1?.new_table?.name,
      option2: aiSuggestions?.option_2?.merged_table?.name
    });
    
    // Check option 1 first (prefer it if available and not explicitly rejected)
    if (aiSuggestions?.option_1?.new_table) {
      const tableName = aiSuggestions.option_1.new_table.name;
      const normalizedName = normalizeTableName(tableName);
      if (!normalizedRejected.includes(normalizedName)) {
        selectedOption = aiSuggestions.option_1;
        isOption1 = true;
        console.log('Selected option 1:', tableName);
      } else {
        console.log('Option 1 rejected (user explicitly rejected):', tableName);
      }
    }
    
    // Fall back to option 2 if option 1 was rejected or unavailable
    if (!selectedOption && aiSuggestions?.option_2?.merged_table) {
      const tableName = aiSuggestions.option_2.merged_table.name;
      const normalizedName = normalizeTableName(tableName);
      if (!normalizedRejected.includes(normalizedName)) {
        selectedOption = aiSuggestions.option_2;
        isOption1 = false;
        console.log('Selected option 2:', tableName);
      } else {
        console.log('Option 2 rejected (user explicitly rejected):', tableName);
      }
    }
    
    if (!selectedOption) {
      // Both options were explicitly rejected by user
      console.log('No valid suggestion available - both options explicitly rejected by user');
      setSuggestionNodes([]);
      setSuggestionEdges([]);
      return;
    }
    
    // Get the table from the selected option
    const table = selectedOption.new_table || selectedOption.merged_table;
    
    if (table) {
      // Find a smart position that doesn't overlap
      const existingNodes = nodes;
      const maxX = Math.max(...existingNodes.map(n => n.position.x), 0);
      const maxY = Math.max(...existingNodes.map(n => n.position.y), 0);
      
      // Calculate fixed size based on fields like regular tables
      const fieldCount = (table.fields || []).length;
      const fixedWidth = 300;
      const fixedHeight = Math.max(200, 120 + fieldCount * 32);
      
      // Use different colors for option 1 vs option 2
      const borderColor = isOption1 ? '#3b82f6' : '#10b981';
      const shadowColor = isOption1 ? 'rgba(59, 130, 246, 0.4)' : 'rgba(16, 185, 129, 0.4)';
      const yPosition = isOption1 ? 50 : 350;
      
      const suggestionNode: Node = {
        id: `suggestion_${table.name}`,
        type: 'tableNode',
        position: { x: maxX + 450, y: yPosition },
        data: {
          tableName: table.name,
          fields: table.fields || [],
          color: { bg: 'hsl(var(--card))', border: borderColor, text: 'hsl(var(--foreground))' },
          isSuggestion: true,
          originalTable: table,
          onReject: handleRejectSuggestion,
        },
        selectable: true,
        draggable: true,
        width: fixedWidth,
        height: fixedHeight,
        style: {
          opacity: 0.6,
          border: `2px dashed ${borderColor}`,
          boxShadow: `0 0 16px ${shadowColor}`,
          cursor: 'pointer',
          width: fixedWidth,
          height: fixedHeight,
        },
      };
      
      setSuggestionNodes([suggestionNode]);

      // Create edges for connections
      const newEdges: Edge[] = (selectedOption.connections || []).map((conn: any, idx: number) => ({
        id: `suggestion_edge_${idx}`,
        source: `suggestion_${table.name}`,
        target: conn.to,
        type: 'straight' as const,
        animated: false,
        markerEnd: {
          type: 'arrowclosed' as const,
          width: 20,
          height: 20,
          color: borderColor,
        },
        style: {
          stroke: borderColor,
          strokeWidth: 2,
          opacity: 0.5,
          strokeDasharray: '8,4',
        },
      }));
      setSuggestionEdges(newEdges);
    }
  }, [aiSuggestions, isLoadingSuggestions, handleRejectSuggestion, nodes, rejectedSuggestions, previouslySuggested]);

  // Convert a ghost node into a regular table node
  const convertGhostToRealTable = useCallback((ghostNode: Node): Node => {
    const nodeData = ghostNode.data as TableNodeData & { isSuggestion?: boolean; originalTable?: any };
    const tableName = nodeData.originalTable?.name || nodeData.tableName || ghostNode.id.replace('suggestion_', '');
    
    // Get a color for the new table (same as manual creation)
    const color = colorPalette[nodes.length % colorPalette.length];
    
    // Ensure fields are properly formatted (same structure as manual creation)
    let fields = nodeData.originalTable?.fields || nodeData.fields || [];
    
    // Ensure fields is an array and each field has required properties
    if (!Array.isArray(fields)) {
      fields = [];
    }
    
    // Normalize fields to match expected structure (same as manual table creation)
    fields = fields.map((field: any) => {
      // Ensure field is an object
      if (!field || typeof field !== 'object') {
        return {
          name: 'field',
          type: 'string',
          required: true,
          primary_key: false,
        };
      }
      
      // Normalize field properties (normalized values take precedence)
      return {
        ...field, // Keep all original properties first
        name: field.name || 'field',
        type: field.type || 'string',
        required: field.required !== undefined ? Boolean(field.required) : true,
        primary_key: Boolean(field.primary_key || false),
        unique: Boolean(field.unique || false),
        foreign_key: field.foreign_key || undefined,
      };
    });
    
    // Create node exactly like manual table creation
    const realNode: Node = {
      id: tableName,
      type: 'tableNode',
      position: ghostNode.position || { x: 100, y: 100 },
      data: {
        tableName: tableName,
        fields: fields,
        color: color,
        onSizeChange: handleNodeSizeChange,
        onConnect: handleConnect,
        onFieldsChange: handleFieldsChange,
        currentNodeId: tableName,
        // allTables will be set when node is added (same as manual creation)
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
    try {
      const nodeData = node.data as TableNodeData & { isSuggestion?: boolean; originalTable?: any };
      
      // Check if this is a suggestion node
      if (nodeData.isSuggestion && nodeData.originalTable) {
        console.log('Accepting suggestion node:', node.id);
        
        // Convert ghost to real table (exactly like manual creation)
        const realNode = convertGhostToRealTable(node);
        
        // Validate the node before adding
        if (!realNode.id || !realNode.data?.tableName) {
          console.error('Invalid node structure:', realNode);
          return;
        }
        
        // Add the real node to the main nodes array (same pattern as addNewTable)
        setNodes((prevNodes) => {
          // Check if node with this ID already exists
          if (prevNodes.some(n => n.id === realNode.id)) {
            console.warn(`Node with id ${realNode.id} already exists`);
            return prevNodes;
          }
          
          const allNodes = [...prevNodes, realNode];
          // Update allTables for all nodes including the new one (same as manual creation)
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
                id: `${realNode.id}-${edge.target}-${Date.now()}`,
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
        
        // Remove the suggestion from the ghosts and clear AI suggestions to prevent regeneration
        setSuggestionNodes([]);
        setSuggestionEdges([]);
        setAiSuggestions(null);
        
        // Also add the table name to rejected suggestions so it won't be suggested again
        const tableName = nodeData.originalTable?.name || nodeData.tableName || node.id.replace('suggestion_', '');
        setRejectedSuggestions(prev => {
          if (!prev.includes(tableName)) {
            return [...prev, tableName];
          }
          return prev;
        });
      }
    } catch (error) {
      console.error('Error accepting suggestion node:', error);
      // Don't crash - just log the error
    }
  }, [suggestionEdges, convertGhostToRealTable]);

  const onNodesChange = useCallback((changes: any) => {
    // Update real nodes
    setNodes((nds) => {
      const updated = [...nds];
      changes.forEach((change: any) => {
        const index = updated.findIndex((n) => n.id === change.id);
        if (index !== -1) {
          if (change.type === 'position' && change.position) {
            updated[index] = { ...updated[index], position: change.position };
          } else if (change.type === 'resize' && change.dimensions) {
            updated[index] = {
              ...updated[index],
              width: change.dimensions.width,
              height: change.dimensions.height,
            };
          } else if (change.type === 'select') {
            updated[index] = { ...updated[index], selected: change.selected };
          }
        }
      });
      return updated;
    });

    // Update suggestion nodes (so dragging them persists)
    setSuggestionNodes((snds) => {
      const updated = [...snds];
      changes.forEach((change: any) => {
        const index = updated.findIndex((n) => n.id === change.id);
        if (index !== -1) {
          if (change.type === 'position' && change.position) {
            updated[index] = { ...updated[index], position: change.position };
          } else if (change.type === 'resize' && change.dimensions) {
            updated[index] = {
              ...updated[index],
              width: change.dimensions.width,
              height: change.dimensions.height,
            };
          } else if (change.type === 'select') {
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
        
        // Normalize fields - preserve all field properties
        fields = fields.map((field: any) => {
          const normalizedField: any = {
            name: field.name,
            type: field.type,
            primary_key: field.primaryKey || field.primary_key || false,
            required: field.required !== undefined ? field.required : true,
          };
          
          // Preserve all optional properties
          if (field.unique !== undefined) normalizedField.unique = field.unique;
          if (field.default !== undefined) normalizedField.default = field.default;
          if (field.autoIncrement !== undefined) normalizedField.auto_increment = field.autoIncrement;
          if (field.auto_increment !== undefined) normalizedField.auto_increment = field.auto_increment;
          if (field.length !== undefined) normalizedField.length = field.length;
          if (field.precision !== undefined) normalizedField.precision = field.precision;
          if (field.scale !== undefined) normalizedField.scale = field.scale;
          if (field.min !== undefined) normalizedField.min = field.min;
          if (field.max !== undefined) normalizedField.max = field.max;
          if (field.minLength !== undefined) normalizedField.min_length = field.minLength;
          if (field.maxLength !== undefined) normalizedField.max_length = field.maxLength;
          if (field.enum && field.enum.length > 0) normalizedField.enum = field.enum;
          if (field.check) normalizedField.check = field.check;
          
          // Preserve foreign_key if it exists (with onDelete/onUpdate)
          if (field.foreign_key) {
            normalizedField.foreign_key = {
              table: field.foreign_key.table,
              field: field.foreign_key.field || 'id',
              onDelete: field.foreign_key.onDelete || 'RESTRICT',
              onUpdate: field.foreign_key.onUpdate || 'RESTRICT',
            };
          } else if (field.foreignKey) {
            // Handle legacy foreignKey format
            normalizedField.foreign_key = {
              table: field.foreignKey.table,
              field: field.foreignKey.field || 'id',
              onDelete: field.foreignKey.onDelete || 'RESTRICT',
              onUpdate: field.foreignKey.onUpdate || 'RESTRICT',
            };
          }
          
          return normalizedField;
        });
        
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
      // Edges use node IDs which match entity names (since nodes are created with id: entity.name)
      const targetToSourceMap = new Map<string, string>();
      edges.forEach(edge => {
        if (edge.target && edge.source) {
          // Get the entity name from the target node
          const targetNode = nodes.find(n => n.id === edge.target);
          const sourceNode = nodes.find(n => n.id === edge.source);
          if (targetNode && sourceNode) {
            const targetEntityName = (targetNode.data as TableNodeData).tableName || targetNode.id;
            const sourceEntityName = (sourceNode.data as TableNodeData).tableName || sourceNode.id;
            targetToSourceMap.set(targetEntityName, sourceEntityName);
          }
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
                  field: 'id',
                  onDelete: 'RESTRICT',
                  onUpdate: 'RESTRICT',
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
                field: 'id',
                onDelete: 'RESTRICT',
                onUpdate: 'RESTRICT',
              },
            };
          }
        }
      });
      
      // Ensure we have a valid schema structure
      if (!schema) {
        throw new Error('No schema provided');
      }
      
      const updatedSchema = {
        ...schema,
        entities: updatedEntities,
      };
      
      // Validate the schema has required fields
      if (!updatedSchema.entities || updatedSchema.entities.length === 0) {
        throw new Error('Schema must have at least one entity');
      }
      
      // Validate each entity has required fields
      updatedSchema.entities.forEach((entity: any, idx: number) => {
        if (!entity.name) {
          throw new Error(`Entity at index ${idx} is missing a name`);
        }
        if (!entity.fields || !Array.isArray(entity.fields)) {
          throw new Error(`Entity "${entity.name}" is missing fields array`);
        }
      });
      
      console.log('Updated schema:', updatedSchema);
      onSchemaUpdate(updatedSchema);
    } catch (error) {
      console.error('Error in handleUpdateSchema:', error);
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      alert(`Error updating schema: ${errorMessage}`);
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
      {/* Button Group - Top Right */}
      <div className="absolute top-4 right-4 z-50 flex items-center gap-2">
        {/* AI Suggestions Button - One-time fetch */}
        <button
          onClick={handleFetchSuggestions}
          disabled={isLoadingSuggestions || !schema?.entities || schema.entities.length === 0}
          className="px-3 py-1.5 rounded-md text-xs transition-all flex items-center gap-2 border border-border bg-background hover:bg-muted text-foreground disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
        >
          {isLoadingSuggestions ? (
            <>
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
              Generating...
            </>
          ) : (
            <>
              <Sparkles className="h-3.5 w-3.5" />
              Get AI Suggestions
            </>
          )}
        </button>
        
        {/* Add Table Button */}
        <button
          onClick={addNewTable}
          className="border border-border bg-background hover:bg-muted text-foreground px-3 py-1.5 rounded-md text-xs transition-colors flex items-center gap-2 shadow-sm"
        >
          <Plus className="h-3.5 w-3.5" />
          Add Table
        </button>
      </div>
      
      {/* Update Schema Button */}
      {onSchemaUpdate && (
        <button
          onClick={handleUpdateSchema}
          className="absolute top-4 left-4 z-50 border border-border bg-background hover:bg-muted text-foreground px-3 py-1.5 rounded-md text-xs transition-colors flex items-center gap-2 shadow-sm"
        >
          Update Schema
        </button>
      )}
      
      <ReactFlow
        nodes={(() => {
          // Only show suggestions if loading is complete
          const shouldShowSuggestions = aiSuggestions && !isLoadingSuggestions;
          const finalNodes = shouldShowSuggestions ? [...nodes, ...suggestionNodes] : nodes;
          console.log('Rendering ReactFlow with nodes:', { 
            nodeCount: finalNodes.length, 
            suggestionNodeCount: suggestionNodes.length,
            hasSuggestions: !!aiSuggestions,
            isLoadingSuggestions
          });
          return finalNodes;
        })()}
        edges={(() => {
          const shouldShowSuggestions = aiSuggestions && !isLoadingSuggestions;
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
        <Background variant={BackgroundVariant.Dots} gap={40} size={1.5} />
        <Controls className="bg-background border border-border rounded-md shadow-sm [&_button]:bg-background [&_button:hover]:bg-muted [&_button]:text-foreground [&_button]:border [&_button]:border-border [&_button]:w-7 [&_button]:h-7 [&_button_svg]:w-3.5 [&_button_svg]:h-3.5 [&_button_svg]:text-foreground" />
      </ReactFlow>
    </div>
  );
};
