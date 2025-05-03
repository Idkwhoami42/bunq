import { Request, Response, NextFunction } from 'express';
import { sql } from '../db'; // Adjust the path if necessary

// Define a type for the user object you expect from the OAuth provider
interface UserInfo {
  id: string; // Or number, depending on your user ID type
  email: string;
  // Add other relevant user properties
}

// Extend the Request interface to include the user information
declare global {
  namespace Express {
    interface Request {
      user?: UserInfo;
    }
  }
}


export const authMiddleware = async (req: Request, res: Response, next: NextFunction) => {
  const authToken = req.headers.authorization?.split(' ')[1]; // Assuming "Bearer <token>" format

  if (!authToken) {
    return res.status(401).json({ message: 'Authentication token required' });
  }

  try {
    // 1. Validate the token with the external OAuth provider
    //    (This part depends on the specific OAuth provider's API)
    //    For example, using `node-fetch`:
    // const response = await fetch('https://oauth-provider.com/userinfo', {
    //   headers: { Authorization: `Bearer ${authToken}` }
    // });
    // if (!response.ok) {
    //   return res.status(401).json({ message: 'Invalid authentication token' });
    // }
    // const userInfo: UserInfo = await response.json();

    // 2. **For now, simulate token validation and user info retrieval:**
    const userInfo: UserInfo = {
      id: 'simulated-user-id',
      email: 'test@example.com',
    };

    // 3. Check if the user exists in your database, create if not
    const existingUser = await sql`SELECT id FROM users WHERE email = ${userInfo.email}`;

    if (existingUser.length === 0) {
      // Create the user
      await sql`INSERT INTO users (id, email) VALUES (${userInfo.id}, ${userInfo.email})`;
    }

    // 4. Attach the user information to the request object
    req.user = userInfo;

    // 5. Proceed to the next middleware/route handler
    next();

  } catch (error) {
    console.error('Authentication error:', error);
    return res.status(500).json({ message: 'Authentication failed' });
  }
};