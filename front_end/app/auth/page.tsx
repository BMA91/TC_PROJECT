"use client";
import { useState } from "react";
import SignUp from "./signup";
import Login from "./login";
import { Single_Day } from "next/font/google";
export default function Auth() {
  const [state, setState] = useState<"log" | "register">("log");

  return (
    <div className="main h-screen flex flex-row">
      <div className="sider w-1/2 ">
        <div className="Dividing-sections section-1"></div>
        <div className="Dividing-sections section-2"></div>
        <div className="Dividing-sections section-3"></div>
        <div className="Dividing-sections section-4"></div>
        <div className="Dividing-sections section-5"></div>
        <div className="Dividing-sections section-6"></div>
        <div className="Dividing-sections section-7"></div>
        <div className="Dividing-sections section-8"></div>
        <div className="Dividing-sections section-9"></div>
        <div className="Dividing-sections section-10"></div>
        <div
          className="logo-container"
          style={{
            backgroundImage: "url('/images/Group 1.svg')",
            backgroundSize: "cover",
            backgroundPosition: "center",
            backgroundRepeat: "no-repeat",
          }}
        ></div>
      </div>
      <div className="formBody bg-white p-8 flex flex-col w-1/2">
        <div className="SwitchBtn flex justify-center items-center mt-5 mb-20 p-2 w-1/2 mx-auto  rounded-full">
          <button
            className={
              state === "log"
                ? "text-[#2255FF] connect w-1/2 py-2  font-medium rounded-full "
                : "bg-[#2255FF] text-white  connect w-1/2 py-2  font-medium rounded-full "
            }
            onClick={() => setState("register")}
          >
            S'inscrire
          </button>
          <button
            className={
              state === "log"
                ? "bg-[#2255FF] text-white connect w-1/2 py-2  font-medium rounded-full "
                : "text-[#2255FF] connect w-1/2 py-2  font-medium rounded-full "
            }
            onClick={() => {
              setState("log");
            }}
          >
            Se connecter
          </button>
        </div>

        {state === "register" ? (
          <><SignUp />
            
          </>
        ) : (
          <><Login />
            
          </>
        )}
      </div>
    </div>
  );
}
