import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { qrcode } from 'vite-plugin-qrcode'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    qrcode() // Shows QR code in terminal
  ],
  server: {
    host: true, // Allows access from other devices on the network
  }
})
