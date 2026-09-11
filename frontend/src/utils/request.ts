interface RequestArgs{
  endpoint: string;
  method?: "GET" | "POST" | "DELETE" | "PUT";
  body?: unknown;
  query?: Record<string,string>; 
}

async function request<T>({  // Reminder: The fn returns the JSON data, not the raw response
  endpoint, 
  method = "GET", 
  body, 
  query 
}: RequestArgs) : Promise<T> {
  try {

    const baseUrl = "http://localhost:5000"; // would have used import.meta.env.VITE_API_URL

    console.log("baseUrl:", baseUrl);

    // Build query string
    const queryString = query
      ? `?${new URLSearchParams(query).toString()}`
      : "";

    const url = `${baseUrl}${endpoint}${queryString}`;

    const theHeaders = {
        "Content-Type": "application/json",
    }

    // would append the JWT token here when implementing one   

    const options: RequestInit = {
      method,
      headers: theHeaders,
    };
    

    // Only add a body when one exists
    if (body && method !== "GET") {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    // Handle Response Errors here
    if (response.status===204){
      return {} as T;
    }

    // Try to parse JSON
    const data = await response.json();

    // reminder, this fn is returning JSON, not the response itself. 
    return data;
  } catch (error) {
    console.error("Request failed:", error);

    // Let the component that called request() handle the error too
    throw error;
  }
}

export default request;

