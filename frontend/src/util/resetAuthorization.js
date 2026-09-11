import { Navigate } from "react-router-dom";

export function resetAuth()
{
    localStorage.clear();
    window.location.href = "/login";
}