import { useMemo } from 'react';
import { Card } from '@/components/ui/card';

interface SchemaVisualizationProps {
  schema: any; // The generated spec
}

export const SchemaVisualization = ({ schema }: SchemaVisualizationProps) => {
  const tables = useMemo(() => {
    if (!schema?.entities) return [];
    return schema.entities.map((entity: any) => ({
      name: entity.name,
      fields: entity.fields || [],
      foreignKeys: entity.fields?.filter((f: any) => f.foreign_key) || []
    }));
  }, [schema]);

  if (!schema || !schema.entities) {
    return (
      <div className="flex items-center justify-center h-full">
        <p className="text-muted-foreground text-sm">No schema to visualize</p>
      </div>
    );
  }

  return (
    <div className="h-full overflow-auto p-4">
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {tables.map((table: any) => (
          <Card key={table.name} className="p-4 hover:border-primary/50 transition-colors">
            <h3 className="font-bold text-lg mb-3 text-primary capitalize">{table.name}</h3>
            
            <div className="space-y-2">
              {table.fields.map((field: any, idx: number) => (
                <div key={idx} className="flex items-center gap-2 text-sm">
                  <span className={`font-mono flex-1 ${field.primary_key ? 'font-bold text-primary' : ''}`}>
                    {field.name}
                  </span>
                  <span className="text-xs bg-muted px-2 py-0.5 rounded">
                    {field.type}
                  </span>
                  {field.primary_key && (
                    <span className="text-xs bg-blue-500/20 text-blue-600 px-2 py-0.5 rounded">
                      PK
                    </span>
                  )}
                  {field.foreign_key && (
                    <span className="text-xs bg-green-500/20 text-green-600 px-2 py-0.5 rounded">
                      FK
                    </span>
                  )}
                  {!field.required && (
                    <span className="text-xs bg-orange-500/20 text-orange-600 px-2 py-0.5 rounded">
                      NULL
                    </span>
                  )}
                </div>
              ))}
            </div>

            {table.foreignKeys.length > 0 && (
              <div className="mt-4 pt-4 border-t">
                <p className="text-xs font-semibold text-muted-foreground mb-2">Relationships:</p>
                {table.foreignKeys.map((fk: any) => (
                  <div key={fk.name} className="text-xs text-muted-foreground mb-1">
                    → {fk.foreign_key?.table}
                  </div>
                ))}
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
};
