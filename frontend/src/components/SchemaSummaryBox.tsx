import React from 'react';

interface SchemaSummaryBoxProps {
  content: string;
}

export const SchemaSummaryBox: React.FC<SchemaSummaryBoxProps> = ({ content }) => {
  // Skip if content looks like an error message
  if (content.includes('Error:') || content.includes('API configuration error') || 
      content.includes('invalid JSON') || content.includes('Please verify')) {
    return null;
  }
  
  // Simple parsing - look for table names in brackets followed by bullet points
  const lines = content.split('\n');
  const tables: Array<{ name: string; fields: string[] }> = [];
  let currentTable: { name: string; fields: string[] } | null = null;
  
  for (const line of lines) {
    const trimmed = line.trim();
    
    // Check if line is a table name in brackets: [TableName]
    const bracketMatch = trimmed.match(/^\[([^\]]+)\]$/);
    if (bracketMatch) {
      // Save previous table
      if (currentTable && currentTable.fields.length > 0) {
        tables.push(currentTable);
      }
      currentTable = { name: bracketMatch[1], fields: [] };
      continue;
    }
    
    // Check if line is a field (starts with bullet or dash)
    if ((trimmed.startsWith('•') || trimmed.startsWith('-') || trimmed.startsWith('*')) && currentTable) {
      const fieldText = trimmed.replace(/^[•\-\*]\s*/, '').trim();
      if (fieldText && !fieldText.includes('Error:') && !fieldText.includes('API')) {
        currentTable.fields.push(fieldText);
      }
    }
  }
  
  // Add last table
  if (currentTable && currentTable.fields.length > 0) {
    tables.push(currentTable);
  }
  
  // Only show if we found at least one table
  if (tables.length === 0) {
    return null;
  }
  
  return (
    <div className="mt-3 rounded-md border border-border/40 bg-[hsl(var(--card))] overflow-hidden">
      <div className="px-3 py-2 border-b border-border/40 bg-[hsl(var(--background))]/30">
        <h4 className="text-xs font-semibold text-foreground">Database Schema Summary</h4>
      </div>
      <div className="p-3 space-y-4">
        {tables.map((table, idx) => (
          <div key={idx} className="space-y-1.5">
            <h5 className="text-sm font-semibold text-foreground capitalize">{table.name}</h5>
            <ul className="space-y-1 list-none ml-0">
              {table.fields.map((field, fIdx) => (
                <li key={fIdx} className="text-xs text-muted-foreground flex items-start gap-1.5">
                  <span className="text-muted-foreground/60">•</span>
                  <span>{field}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
};
