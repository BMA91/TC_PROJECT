"use client";

import { useState, useContext, useEffect } from "react";
import { useRouter } from "next/navigation";
import { LoginContext } from "../../layout";
import Link from "next/link";
import Image from "next/image";

const ticketTypes = [
  { label: "Legal, Regulatory, and Commercial Frameworks", value: "Legal, Regulatory, and Commercial Frameworks" },
  { label: "Support and Reference Documentation", value: "Support and Reference Documentation" },
  { label: "Operational and Practical User Guides", value: "Operational and Practical User Guides" },
  { label: "Other", value: "Other" },
];

const logo = "/images/logo.svg";
const userp = "/images/user.svg";

export default function TicketsPage() {
  const context = useContext(LoginContext);
  const { loginData, setLoginData } = context ?? {};
  const router = useRouter();

  const [menu, setMenu] = useState(false);
  const [formData, setFormData] = useState({
    ticketType: "",
    title: "",
    description: "",
    attachment: null,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!loginData) router.push("/auth");
  }, [loginData]);

  if (!context) return null;

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleFileChange = (e) => {
    // File uploads are not supported by the backend ticket create endpoint.
    // We keep the handler but do not send files to the backend.
    setFormData((prev) => ({ ...prev, attachment: e.target.files[0] }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // Map frontend ticketType to backend expected ticket_type values
      let ticket_type = formData.ticketType;
      if (ticket_type === "Other") ticket_type = "other";

      const payload = {
        title: formData.title,
        description: formData.description,
        ticket_type: ticket_type,
      };

      const clientId = loginData?.id;
      // Use the same server route as the signup page (Next.js API)
      const url = `/api/tickets?client_id=${clientId}`;

      const res = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const resJson = await res.json().catch(() => null);
      if (!res.ok) {
        alert("Ticket creation failed: " + JSON.stringify(resJson));
        throw new Error("Failed to create ticket");
      }

      const ticket = resJson;
      alert("Ticket créé avec succès ! ID: " + ticket.id);

      setFormData({
        ticketType: "",
        title: "",
        description: "",
        attachment: null,
      });
    } catch {
      alert("Erreur lors de la création du ticket");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main>
      <div className="bg-[#0C2155] h-10 w-full"></div>

      <nav className="px-6 py-4 flex items-center">
        <div className="flex items-center gap-2">
          <Image src={logo} alt="Doxa logo" width={32} height={32} />
          <span className="text-2xl font-bold text-blue-900">Doxa</span>
        </div>

        <div className="flex gap-8 ml-24">
          <a href="/dashboard" className="text-blue-900 font-medium">
            Home
          </a>
          <a className="text-blue-900 font-medium">À propos</a>
          <a className="text-blue-900 font-medium">Tarification</a>
          <a className="text-blue-900 font-medium">Aide</a>
        </div>

        <Link
          href="/dashboard/tickets"
          className="ml-auto bg-blue-600 px-6 py-2 text-white rounded-lg hover:bg-blue-700"
        >
          Vos tickets
        </Link>

        <div className="relative pl-6">
          <button
            onClick={() => setMenu(!menu)}
            className="flex items-center gap-2"
          >
            <Image src={userp} alt="Profile" width={32} height={32} />
            Profile
          </button>

          {menu && (
            <div className="absolute right-0 mt-3 w-56 bg-[#0C2155] text-white p-4 rounded-xl">
              <p className="font-semibold">{loginData?.address ?? "User"}</p>
              <p className="text-[#AAC7FF] text-sm">{loginData?.role ?? "User"}</p>
              <hr className="my-3 border-white/30" />
              <button className="border border-white rounded px-2 py-1 mb-3">
                Modify
              </button>
              <hr className="my-3 border-white/30" />
              <button
                onClick={() => {
                  try {
                    localStorage.removeItem("isAuth");
                    localStorage.removeItem("userData");
                  } catch (e) {}
                  setLoginData?.(null);
                  router.push("/auth");
                }}
                className="text-red-400 text-left"
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </nav>

      <div className="max-w-4xl mx-auto px-8 py-14">
        <h1 className="text-3xl font-bold text-[#1E1E4B] mb-10">
          Demander à Doxa
        </h1>

        <form onSubmit={handleSubmit} className="space-y-8">
          <fieldset className="space-y-3">
            <legend className="font-medium mb-2">Type de ticket</legend>
            {ticketTypes.map((type) => (
              <label key={type.value} className="flex items-center gap-3">
                <input
                  type="radio"
                  name="ticketType"
                  value={type.value}
                  checked={formData.ticketType === type.value}
                  onChange={handleChange}
                  required
                />
                {type.label}
              </label>
            ))}
          </fieldset>

          <input
            name="title"
            value={formData.title}
            onChange={handleChange}
            placeholder="Titre"
            className="w-full border rounded px-4 py-2"
            required
          />

          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            rows={4}
            className="w-full border rounded px-4 py-2"
            placeholder="Description"
            required
          />

          <input type="file" onChange={handleFileChange} />

          <button
            type="submit"
            className="bg-blue-600 text-white px-10 py-2 rounded-lg"
            disabled={loading}
          >
            {loading ? "Création..." : "Soumettre"}
          </button>
        </form>
      </div>
    </main>
  );
}
