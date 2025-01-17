import React, { useState } from "react";
import API from "../services/api";
import { useAuth } from "../hooks/useAuth";
import { Navigate } from "react-router-dom";

const Login = () => {
    const { user, login } = useAuth();
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");


    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const { data } = await API.post("auth/login", { username, password });
            login();
            localStorage.setItem("token", data.access_token);
            localStorage.setItem("username", data.username);
            console.log(data);
        } catch (error) {
            console.error("Login failed");
        }
    };

    if (user) {
        return <Navigate to="/dashboard" />;
    }

    return (
        <form onSubmit={handleSubmit} className="max-w-md mx-auto p-4 space-y-4">
            <h1 className="text-2xl font-bold">Login</h1>
            <input
                type="text"
                placeholder="username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full p-2 border rounded"
            />
            <input
                type="password"
                placeholder="Password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full p-2 border rounded"
            />
            <button type="submit" className="w-full bg-blue-500 text-white p-2 rounded">
                Login
            </button>
        </form>
    );
};

export default Login;
