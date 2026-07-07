interface SqlUploadPayload {
    sql_content: string;
}

interface SqlUploadResponse {
    message?: string;
    key?: string;
    error?: string;
}

async function uploadSqlFile(
    sqlContent: string,
    apiUrl: string,
    apiKey?: string
): Promise<SqlUploadResponse> {
    const payload: SqlUploadPayload = {
        sql_content: sqlContent
    };

    const headers: Record<string, string> = {
        "Content-Type": "application/json"
    };

    if (apiKey) {
        headers["x-api-key"] = apiKey;
    }

    console.log(`[uploadSchema] POST ${apiUrl} (${sqlContent.length} chars)`);

    const response = await fetch(apiUrl, {
        method: "POST",
        headers,
        body: JSON.stringify(payload)
    });

    console.log(`[uploadSchema] response status: ${response.status}`);

    if (!response.ok) {
        const errorText = await response.text();
        console.error(`[uploadSchema] request failed: ${response.status} - ${errorText}`);
        throw new Error(`Request failed with status ${response.status}: ${errorText}`);
    }

    const result: SqlUploadResponse = await response.json();
    console.log("[uploadSchema] response body:", result);
    return result;
}

export function uploadSchema(sqlContent: string, filename: string = "schema.sql") {
  console.log(`[uploadSchema] called with filename="${filename}"`);

  uploadSqlFile(
    sqlContent,
    "https://ijanvqym43.execute-api.us-east-1.amazonaws.com/dev/test"
    // "YOUR_API_KEY" // pass this if you secured it with an API key
)
    .then(result => console.log("[uploadSchema] Success:", result))
    .catch(err => console.error("[uploadSchema] Error:", err));
}
