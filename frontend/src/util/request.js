import { resetAuth } from "./resetAuthorization";

async function request({ endpoint, method = "GET", body, query }) {
  try {
    const baseUrl = import.meta.env.VITE_API_URL;

    console.log("baseUrl:", baseUrl);

    // Build query string
    const queryString = query
      ? `?${new URLSearchParams(query).toString()}`
      : "";

    const url = `${baseUrl}${endpoint}${queryString}`;

    // grabbing token here
    const theHeaders = {
        "Content-Type": "application/json",
    }

    
    const token = localStorage.getItem('token');
    if(token)
    {
      theHeaders['Authorization'] = `Bearer ${token}`;
    }

    const options = {
      method,
      headers: theHeaders,
    };
    

    // Only add a body when one exists
    if (body && method !== "GET") {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    // Try to parse JSON
    const data = await response.json();

    // fetch() doesn't reject on HTTP errors like 400 or 500,
    // so we handle them ourselves.
    if(response.status===401 || response.status===403)
    {
      resetAuth();
      throw new Error(
        data.message || `Expired Token,' ${response.status}`
      );
    }

    if (!response.ok) {
      throw new Error(
        data.message || `Request failed with status ${response.status}`
      );
    }

    return data;
  } catch (error) {
    console.error("Request failed:", error);

    // Let the component that called request() handle the error too
    throw error;
  }
}

export default request;

