import { withAuth } from "next-auth/middleware"

export default withAuth({
  pages: {
    signIn: "/login",
    verifyRequest: "/2fa"
  }
})

export const config = { matcher: ["/dashboard", "/2fa"] }
