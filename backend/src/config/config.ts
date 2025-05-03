import dotenv from 'dotenv';

dotenv.config();

interface Config {
  port: number;
  nodeEnv: string;
  googlePlacesApiKey: string | undefined;
}

const config: Config = {
  port: Number(process.env.PORT) || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  googlePlacesApiKey: process.env.GOOGLE_PLACES_API_KEY,
};

export default config;