import React, { createContext, useContext, useState, ReactNode } from "react";

type UserInfo = {
  age?: number;
  gender?: string;
  location?: string;
  budgetMin?: number;
  budgetMax?: number;
  categories?: string[];
  interests?: string;
};

type UserContextType = {
  userInfo: UserInfo;
  setUserInfo: (info: UserInfo) => void;
  sessionId: string | null;
  setSessionId: (id: string | null) => void;
};

const UserContext = createContext<UserContextType | undefined>(undefined);

export const UserProvider = ({ children }: { children: ReactNode }) => {
  const [userInfo, setUserInfo] = useState<UserInfo>({});
  const [sessionId, setSessionIdState] = useState<string | null>(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("sessionId");
    }
    return null;
  });

  const setSessionId = (id: string | null) => {
    setSessionIdState(id);
    if (typeof window !== "undefined") {
      if (id) {
        localStorage.setItem("sessionId", id);
      } else {
        localStorage.removeItem("sessionId");
      }
    }
  };

  return (
    <UserContext.Provider value={{ userInfo, setUserInfo, sessionId, setSessionId }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error("useUser must be used within a UserProvider");
  }
  return context;
};
