import React, { useEffect, useState } from "react";
import { useLocation } from "wouter";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useMutation } from "@tanstack/react-query";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { insertShoppingQuerySchema } from "@/shared/schema";
import { apiRequest } from "@/lib/queryClient";
import { useToast } from "@/hooks/use-toast";
import { useUser } from "@/context/UserContext";
import { 
  Search, 
  ArrowLeft, 
  Sparkles,
  Star,
  Calendar,
  Award
} from "lucide-react";
import { z } from "zod";

const categories = [
  { id: "art-decor", label: "Art & Decor" },
  { id: "automotive", label: "Automotive & Accessories" },
  { id: "baby-maternity", label: "Baby & Maternity" },
  { id: "bags-accessories", label: "Bags & Accessories" },
  { id: "beauty", label: "Beauty & Personal Care" },
  { id: "books-stationery", label: "Books & Stationery" },
  { id: "cleaning", label: "Cleaning & Household Supplies" },
  { id: "diy-crafts", label: "DIY & Crafts" },
  { id: "eco-friendly", label: "Eco-Friendly Living" },
  { id: "electronics", label: "Electronics" },
  { id: "fashion", label: "Fashion & Apparel" },
  { id: "footwear", label: "Footwear" },
  { id: "gaming", label: "Gaming & Entertainment" },
  { id: "garden-outdoor", label: "Garden & Outdoor" },
  { id: "grocery", label: "Grocery & Gourmet Food" },
  { id: "health-wellness", label: "Health & Wellness" },
  { id: "home-kitchen", label: "Home & Kitchen" },
  { id: "jewelry-watches", label: "Jewelry & Watches" },
  { id: "luxury", label: "Luxury & Designer Goods" },
  { id: "music-instruments", label: "Music & Instruments" },
  { id: "office", label: "Office & Work Essentials" },
  { id: "pet-supplies", label: "Pet Supplies" },
  { id: "smart-home", label: "Smart Home Devices" },
  { id: "sports-fitness", label: "Sports & Fitness" },
  { id: "sustainable", label: "Sustainable Products" },
  { id: "tech-accessories", label: "Tech Accessories" },
  { id: "tools-improvement", label: "Tools & Home Improvement" },
  { id: "toys-kids", label: "Toys & Kids" },
  { id: "travel-luggage", label: "Travel & Luggage" },
  { id: "vintage-collectibles", label: "Vintage & Collectibles" }
];

const occasions = [
  "Personal Use",
  "Birthday Gift", 
  "Anniversary",
  "Wedding",
  "Holiday Gift",
  "Work/Professional",
  "Special Occasion",
  "Home Improvement",
  "Back to School",
  "Seasonal",
  "Travel",
  "Fitness/Health",
  "Hobby/Recreation"
];

const formSchema = insertShoppingQuerySchema.extend({
  occasion: z.string().min(1, "Occasion is required"),
  brands: z.string().optional(),
  query: z.string().min(10, "Please describe what you're looking for (minimum 10 characters)"),
});

type FormData = z.infer<typeof formSchema>;

const BACKEND_BASE_URL = "http://localhost:5000";

export default function Shopping() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const { userInfo, sessionId } = useUser();
  const [showRecommendations, setShowRecommendations] = useState(false);
  const [currentQuery, setCurrentQuery] = useState<any>(null);
  const [activeProductIndex, setActiveProductIndex] = useState<number | null>(null);

  // Redirect to user-info if sessionId is missing
  React.useEffect(() => {
    if (!sessionId) {
      toast({
        title: "Session Missing",
        description: "Please provide your user information first.",
        variant: "default",
      });
      setLocation("/user-info");
    }
  }, [sessionId, setLocation, toast]);

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      query: "",
      occasion: "",
      brands: "",
    },
  });

  const generateRecommendationsMutation = useMutation({
    mutationFn: async (shoppingData: FormData) => {
      if (!sessionId) {
        throw new Error("Session ID is missing. Please provide user info.");
      }
      const shoppingInput = {
        occasion: shoppingData.occasion,
        brandsPreferred: shoppingData.brands,
        shoppingInput: shoppingData.query,
      };
      const combinedData = {
        session_id: sessionId,
        shopping_input: shoppingInput,
      };
      const response = await apiRequest("POST", "/api/shopping-recommendations", combinedData);
      return response.json();
    },
    onSuccess: (query) => {
      setCurrentQuery(query);
      setShowRecommendations(true);

      setTimeout(() => {
        const recommendationsSection = document.getElementById('recommendations-section');
        if (recommendationsSection) {
          recommendationsSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
          });
        }
      }, 100);

      toast({
        title: "Recommendations Generated",
        description: "Your personalized recommendations are ready!",
      });
    },
    onError: (error: any) => {
      toast({
        title: "Error",
        description: error.message || "Failed to generate recommendations",
        variant: "destructive",
      });
    },
  });

  const onSubmit = (data: FormData) => {
    generateRecommendationsMutation.mutate(data);
  };


  const getCategoryColor = (category: string) => {
    switch (category.toLowerCase()) {
      case 'best match':
        return 'bg-primary/10 text-primary';
      case 'best value':
        return 'bg-primary/20 text-primary';
      case 'premium':
        return 'bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400';
      default:
        return 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300';
    }
  };

  const handleGetMoreRecommendations = () => {
    setShowRecommendations(false);
    setTimeout(() => {
      window.scrollTo({ top: 0, left: 0, behavior: "smooth" });
    }, 50);
  };

  return (
    <div className="py-8 bg-background dark:bg-background min-h-screen">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {userInfo && Array.isArray(userInfo.categories) && userInfo.categories.length > 0 && (
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 dark:text-foreground mb-2">
              Welcome! Shopping for: {
                (userInfo.categories as string[])
                  .map((cat) =>
                categories.find(c => c.id === cat)?.label || cat
                  ).join(", ")
              }
            </h1>
            <p className="text-gray-600 dark:text-muted-foreground">Tell us what you're looking for today</p>
          </div>
        )}

        <Card className="bg-white dark:bg-card rounded-xl shadow-lg border border-gray-100 dark:border-border mb-8">
        <CardHeader className="bg-yellow-400 text-white">
          <CardTitle className="text-2xl font-heading mb-2">Enter Your Shopping Input</CardTitle>
          <p className="text-white/90 font-body">Describe what you're looking for and we'll find the perfect recommendations</p>
        </CardHeader>

          <CardContent className="p-8">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                <div className="grid md:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="occasion"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
                          <Calendar className="text-primary mr-2 h-4 w-4" />
                          Shopping Occasion *
                        </FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger className="form-field">
                              <SelectValue placeholder="Select an occasion" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {occasions.map((occasion) => (
                              <SelectItem key={occasion} value={occasion}>
                                {occasion}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="brands"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
                          <Award className="text-primary mr-2 h-4 w-4" />
                          Brands Preferred
                        </FormLabel>
                        <FormControl>
                          <Input
                            {...field}
                            placeholder="Enter preferred brands (optional)"
                            className="form-field"
                            autoComplete="off"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <FormField
                  control={form.control}
                  name="query"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel className="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
                        <Search className="text-primary mr-2 h-4 w-4" />
                        What are you looking for? *
                      </FormLabel>
                      <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                        You can enter this in any language and the AI will help you find products.
                      </p>
                      <FormControl>
                        <Textarea
                          {...field}
                          rows={5}
                          placeholder="Describe your shopping needs in detail..."
                          className="form-field"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <div className="flex justify-between items-center pt-6 border-t border-gray-200 dark:border-gray-700">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setLocation('/user-info')}
                    className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                  >
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back
                  </Button>
                  <Button
                    type="submit"
                    disabled={generateRecommendationsMutation.isPending}
                    className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    {generateRecommendationsMutation.isPending ? (
                      <div className="spinner mr-2"></div>
                    ) : (
                      <Sparkles className="mr-2 h-4 w-4" />
                    )}
                    Get Recommendations
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>

        {showRecommendations && currentQuery && (
          <Card 
            id="recommendations-section"
            className="bg-white dark:bg-card rounded-xl shadow-lg border border-gray-100 dark:border-border"
          >
            <CardHeader className="bg-yellow-400 text-white">
              <CardTitle className="text-2xl font-bold mb-2">AI Recommendations</CardTitle>
              <p className="text-white/90">Personalized suggestions based on your preferences</p>
            </CardHeader>

            <CardContent className="p-8">
              {generateRecommendationsMutation.isPending ? (
                <div className="text-center py-12">
                  <div className="spinner mx-auto mb-4"></div>
                  <p className="text-gray-600 dark:text-muted-foreground">Analyzing your preferences and generating recommendations...</p>
                </div>
              ) : (
                <div>
                  <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
                    {currentQuery.products?.map((recommendation: any, index: number) => (
                      <div
                        key={index}
                        className={`bg-gray-50 dark:bg-muted rounded-lg p-6 border border-gray-200 dark:border-border transition-all duration-300 ${
                          activeProductIndex === index
                            ? "shadow-4xl -translate-y-3 z-20"
                            : "hover:shadow-lg"
                        }`}
                        onMouseEnter={() => setActiveProductIndex(index)}
                        onMouseLeave={() => setActiveProductIndex(null)}
                      >
                        <div className="flex items-center justify-between mb-4">
                          <Badge className={getCategoryColor(recommendation.category)}>
                            {recommendation.category}
                          </Badge>
                          <span className="text-2xl font-bold text-gray-900 dark:text-foreground">
                            {recommendation.currency}{recommendation.price}
                          </span>
                        </div>
                        <h4 className="font-semibold text-gray-900 dark:text-foreground mb-2">
                          {recommendation.name}
                        </h4>
                        <img
                          src={
                            recommendation.image?.startsWith("http")
                              ? recommendation.image
                              : BACKEND_BASE_URL + recommendation.image
                          }
                          alt={recommendation.name}
                          className="w-full h-48 object-contain mb-4 rounded"
                        />
                        <p className="text-sm text-gray-600 dark:text-muted-foreground mb-4">
                          {recommendation.reasoning}
                        </p>
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            <Star className="text-yellow-400 mr-1 h-4 w-4 fill-current" />
                            <span className="text-sm text-gray-600 dark:text-muted-foreground">
                              {recommendation.rating}
                            </span>
                          </div>
                          <Button 
                            variant="outline"
                            size="sm"
                            className="text-primary border-primary hover:bg-primary/10"
                            onClick={() => window.open(
                              recommendation.buyUrl?.startsWith("http")
                                ? recommendation.buyUrl
                                : BACKEND_BASE_URL + recommendation.buyUrl,
                              "_blank"
                            )}
                          >
                            View Details
                          </Button>
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="flex justify-center mt-8">
                    <Button 
                      variant="outline"
                      onClick={handleGetMoreRecommendations}
                      className="border-primary text-primary hover:bg-primary/10"
                    >
                      Get More Recommendations
                    </Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
