"use client";

import { FormEvent, useState } from "react";
import { api, type Role } from "@/lib/api";
import { useAuth } from "@/lib/auth/AuthProvider";

export default function UsersPage() {
  const { accessToken, hasRole } = useAuth();
  const [form, setForm] = useState({ name: "", email: "", password: "", role: "author" as Role });
  const [message, setMessage] = useState("");
  async function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); if (!accessToken) return; try { await api.createUser(form, accessToken); setMessage("User created."); setForm({ name: "", email: "", password: "", role: "author" }); } catch (error) { setMessage(error instanceof Error ? error.message : "Unable to create user."); } }
  if (!hasRole("admin")) return <main className="admin-content"><div className="empty-state"><h1>Admin access required.</h1><p>Your role does not include user management.</p></div></main>;
  return <main className="admin-content narrow-content"><p className="eyebrow">Administration</p><h1>Build the desk.</h1><p className="muted">Create an account for a new member of the editorial team.</p><form className="editor-form" onSubmit={submit}><label>Name<input value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} required /></label><label>Email<input type="email" value={form.email} onChange={(event) => setForm({ ...form, email: event.target.value })} required /></label><label>Temporary password<input type="password" minLength={12} value={form.password} onChange={(event) => setForm({ ...form, password: event.target.value })} required /></label><label>Role<select value={form.role} onChange={(event) => setForm({ ...form, role: event.target.value as Role })}><option value="author">Author</option><option value="editor">Editor</option><option value="admin">Admin</option><option value="reader">Reader</option></select></label>{message && <p className={message === "User created." ? "form-success" : "form-error"}>{message}</p>}<button className="button button-dark">Create user</button></form></main>;
}
