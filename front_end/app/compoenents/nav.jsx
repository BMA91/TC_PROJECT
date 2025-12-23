"use client";

import { useState } from "react";
import Link from "next/link";
import Image from "next/image";

export default function NavBar({ loginData, logo, userp, menuLinks = [] }) {
  const [menu, setMenu] = useState(false);

  return (
    <nav className="px-6 py-4 flex items-center">
      <div className="flex items-center gap-2">
        <Image src={logo} alt="Logo" width={32} height={32} />
        <span className="text-2xl font-bold text-blue-900">Doxa</span>
      </div>

      <div className="flex gap-8 ml-24">
        {menuLinks.map((link) => (
          <a key={link.href} href={link.href} className="text-blue-900 font-medium">
            {link.label}
          </a>
        ))}
      </div>

      <Link
        href="/dashboard/tickets"
        className="ml-auto bg-blue-600 px-6 py-2 text-white rounded-lg hover:bg-blue-700"
      >
        Vos tickets
      </Link>

      <div className="relative pl-6">
        <button onClick={() => setMenu(!menu)} className="flex items-center gap-2">
          <Image src={userp} alt="Profile" width={32} height={32} />
          Profile
        </button>

        {menu && (
          <div className="absolute right-0 mt-3 w-56 bg-[#0C2155] text-white p-4 rounded-xl">
            <p className="font-semibold">{loginData?.address ?? "User"}</p>
            <p className="text-[#AAC7FF] text-sm">UI/UX Designer</p>

            <hr className="my-3 border-white/30" />

            <button className="border border-white rounded px-2 py-1 mb-3">
              Modify
            </button>

            <hr className="my-3 border-white/30" />

            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <img src="./s" alt="" />
                <button>Notifications</button>
              </div>
              <div className="flex items-center gap-2">
                <img src="./s" alt="" />
                <button>Messages</button>
              </div>

              <hr className="my-2 border-white/30" />

              <div className="flex items-center gap-2">
                <img src="./s" alt="" />
                <button>Aide</button>
              </div>
              <div className="flex items-center gap-2">
                <img src="./s" alt="" />
                <button>Paramètres</button>
              </div>

              <hr className="my-2 border-white/30" />

              <button className="text-red-400 text-left">Logout</button>
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
