// API endpoint types based on the provided specification
export interface ApiEndpoints {
  countries: string
  currencies: string
  userProfile: string
  productCategories: string
  recommendations: string
  products: string
}

export const API_ENDPOINTS: ApiEndpoints = {
  countries: "/api/countries",
  currencies: "/api/currencies",
  userProfile: "/api/user/profile",
  productCategories: "/api/categories",
  recommendations: "/api/recommendations",
  products: "/api/products",
}

export interface UserProfile {
  location: string
  age: string
  gender: string
  categories: string[]
  interests: string
  budgetMin: string
  budgetMax: string
}

export interface Product {
  id: string
  name: string
  price: number
  currency: string
  image: string
  buyUrl: string
  category: string
  rating: number
  description?: string
}

export interface RecommendationRequest {
  userProfile: UserProfile
  shoppingInput: {
    occasion: string
    priceRange: string
    urgency: string
    specificNeeds: string
    style: string
  }
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}
