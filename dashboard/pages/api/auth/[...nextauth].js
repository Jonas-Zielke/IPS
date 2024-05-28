import NextAuth from "next-auth";
import CredentialsProvider from "next-auth/providers/credentials";

// In-Memory storage for 2FA secrets
const userSecrets = {};

export default NextAuth({
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        username: { label: "Username", type: "text" },
        password: { label: "Password", type: "password" },
      },
      authorize: async (credentials) => {
        const adminUser = {
          username: process.env.ADMIN_USERNAME,
          password: process.env.ADMIN_PASSWORD,
        };

        if (
          credentials.username === adminUser.username &&
          credentials.password === adminUser.password
        ) {
          return { id: 1, name: "Admin" };
        }
        return null;
      },
    }),
  ],
  session: {
    jwt: true,
  },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
      }
      return token;
    },
    async session({ session, token }) {
      session.user.id = token.id;
      session.user.secret = userSecrets[token.id] || null;
      return session;
    },
  },
  secret: process.env.NEXTAUTH_SECRET,
  pages: {
    signIn: "/login",
    error: "/auth/error", // Error code passed in query string as ?error=
  },
});
