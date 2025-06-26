import React, { useRef, useState } from "react";
import { useLocation } from "wouter";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { AlertDialog, AlertDialogAction, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle, AlertDialogCancel } from "@/components/ui/alert-dialog";
import { insertUserProfileSchema } from "@/shared/schema";
import { useToast } from "@/hooks/use-toast";
import { useUser } from "@/context/UserContext";
import { 
  User, 
  MapPin, 
  ShoppingBag, 
  ArrowLeft, 
  ArrowRight,
  Upload,
  Download,
  Cake,
  Database,
  Users,
  DollarSign,
  X
} from "lucide-react";
import { z } from "zod";
import { createSessionId } from "@/lib/utils";
import { apiRequest } from "@/lib/queryClient";

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

const countries = [
  { name: "United States", currency: "$" },
  { name: "Canada", currency: "CAD $" },
  { name: "United Kingdom", currency: "£" },
  { name: "Germany", currency: "€" },
  { name: "France", currency: "€" },
  { name: "Italy", currency: "€" },
  { name: "Spain", currency: "€" },
  { name: "Netherlands", currency: "€" },
  { name: "Australia", currency: "AUD $" },
  { name: "Japan", currency: "¥" },
  { name: "South Korea", currency: "₩" },
  { name: "Singapore", currency: "SGD $" },
  { name: "Brazil", currency: "R$" },
  { name: "Mexico", currency: "MXN $" },
  { name: "India", currency: "₹" },
  { name: "China", currency: "¥" },
  { name: "Russia", currency: "₽" },
  { name: "Turkey", currency: "₺" },
  { name: "South Africa", currency: "R" },
  { name: "Egypt", currency: "E£" },
  { name: "Sweden", currency: "kr" },
  { name: "Norway", currency: "kr" },
  { name: "Denmark", currency: "kr" },
  { name: "Finland", currency: "€" },
  { name: "Switzerland", currency: "CHF" },
  { name: "Austria", currency: "€" },
  { name: "Belgium", currency: "€" },
  { name: "Portugal", currency: "€" },
  { name: "Ireland", currency: "€" },
  { name: "New Zealand", currency: "NZD $" }
];

const formSchema = insertUserProfileSchema.extend({
  categories: z.array(z.string()).min(1, "Please select at least one category"),
  age: z.number().min(1, "Age is required").max(120, "Please enter a valid age"),
  gender: z.string().min(1, "Gender is required"),
  location: z.string().min(1, "Location is required"),
  budgetMin: z.number().min(0, "Minimum budget must be 0 or greater"),
  budgetMax: z.number().min(1, "Maximum budget must be greater than 0"),
  interests: z.string().min(10, "Please describe your interests (minimum 10 characters)"),
}).refine((data) => data.budgetMax > data.budgetMin, {
  message: "Maximum budget must be greater than minimum budget",
  path: ["budgetMax"],
});

type FormData = z.infer<typeof formSchema>;

type CustomNumberInputProps = {
  value: number;
  setValue: (v: number) => void;
  min?: number;
  max?: number;
  step?: number;
  className?: string;
  [key: string]: any;
};

function CustomNumberInput({
  value,
  setValue,
  min = 0,
  max = 9999,
  step = 1,
  className = "",
  ...props
}: CustomNumberInputProps) {
  return (
    <div className={`flex items-center h-12 w-full bg-transparent border border-gray-300 dark:border-gray-700 rounded-lg overflow-hidden focus-within:border-yellow-400 ${className}`} {...props}>
      <button
        type="button"
        onClick={() => setValue(Math.max(min, (value || 0) - step))}
        className="w-10 h-12 text-yellow-400 hover:bg-yellow-400/10 transition-colors text-xl font-bold flex items-center justify-center focus:outline-none border-r border-gray-300 dark:border-gray-700"
        tabIndex={-1}
      >
        -
      </button>
      <input
        type="text"
        inputMode="numeric"
        pattern="[0-9]*"
        style={{ appearance: 'textfield', MozAppearance: 'textfield', WebkitAppearance: 'none' }}
        className="form-field no-spinner w-full text-center bg-transparent border-none outline-none text-lg font-semibold text-gray-900 dark:text-white focus:ring-0"
        value={value || ""}
        onChange={e => {
          const val = e.target.value.replace(/[^0-9]/g, '');
          setValue(Math.max(min, Math.min(max, val ? parseInt(val) : 0)));
        }}
      />
      <button
        type="button"
        onClick={() => setValue(Math.min(max, (value || 0) + step))}
        className="w-10 h-12 text-yellow-400 hover:bg-yellow-400/10 transition-colors text-xl font-bold flex items-center justify-center focus:outline-none border-l border-gray-300 dark:border-gray-700"
        tabIndex={-1}
      >
        +
      </button>
    </div>
  );
}

export default function UserInfo() {
  const [, setLocation] = useLocation();
  const { toast } = useToast();
  const { userInfo, setUserInfo, sessionId, setSessionId } = useUser();
  const [selectedCategories, setSelectedCategories] = useState<string[]>([]);
  const [selectedCountry, setSelectedCountry] = useState("");
  const categoriesRef = useRef<HTMLDivElement>(null);
  const [categoriesError, setCategoriesError] = useState<string>("");
  const [showExportPopup, setShowExportPopup] = useState(false);
  const [showExportAfterSubmit, setShowExportAfterSubmit] = useState(false);

  // Initialize selectedCountry from userInfo.location if available
  React.useEffect(() => {
    if (userInfo.location) {
      setSelectedCountry(userInfo.location);
    }
  }, [userInfo.location]);

  const form = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      age: undefined,
      gender: "",
      location: "",
      budgetMin: 0,
      budgetMax: 100,
      categories: [],
      interests: "",
    },
  });

  // Synchronize form's categories field with selectedCategories state
  React.useEffect(() => {
    form.setValue("categories", selectedCategories);
  }, [selectedCategories, form]);

  // Initialize selectedCategories state from form's categories field on form reset or initial load
  React.useEffect(() => {
    const categoriesFromForm = form.getValues("categories") || [];
    setSelectedCategories(categoriesFromForm);
  }, [form]);

  // Watch for form validation errors and scroll to categories if needed
  React.useEffect(() => {
    if (form.formState.errors.categories) {
      setCategoriesError(form.formState.errors.categories.message || "Please select at least one category");
      setTimeout(() => {
        if (categoriesRef.current) {
          categoriesRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 100);
    }
  }, [form.formState.errors.categories]);

  // On import, always navigate to shopping
  const handleImportData = () => {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = async (e) => {
      const file = (e.target as HTMLInputElement).files?.[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = async (e) => {
          try {
            const data = JSON.parse(e.target?.result as string);
            if (data.profile) {
              let importedCategories = data.profile.categories || [];
              if (typeof importedCategories === 'string') {
                importedCategories = [importedCategories];
              }
              importedCategories = importedCategories.filter((id: string) =>
                categories.some((cat) => cat.id === id)
              );
              const importedProfile = { ...data.profile, categories: importedCategories };
              form.reset(importedProfile);
              setSelectedCategories(importedCategories);
              form.setValue("categories", importedCategories);
              setUserInfo(importedProfile);
              if (data.profile.location) {
                setSelectedCountry(data.profile.location);
              }
              if (data.sessionId) {
                setSessionId(data.sessionId);
              }
              
              // Send imported data to backend to store in session
              const currentSessionId = sessionId || data.sessionId || createSessionId();
              try {
                const response = await apiRequest("POST", "/api/user-info", {
                  ...importedProfile,
                  session_id: currentSessionId,
                }, {
                  headers: {
                    "X-Session-Id": currentSessionId,
                  },
                });
                const result = await response.json();
                if (result.status === "success") {
                  setSessionId(result.session_id);
                }
              } catch (error) {
                // error intentionally silenced for clean client
              }
              
              toast({
                title: "Data Imported",
                description: "Your data has been imported successfully!",
              });
              setShowExportAfterSubmit(false);
              setShowExportPopup(false);
              setLocation("/shopping");
            }
          } catch (error) {
            toast({
              title: "Import Error",
              description: "Invalid file format",
              variant: "destructive",
            });
          }
        };
        reader.readAsText(file);
      }
    };
    input.click();
  };

  // On export or close, always navigate to shopping
  const handleExportPopupChange = (open: boolean) => {
    if (!open && showExportAfterSubmit) {
      setShowExportPopup(false);
      setShowExportAfterSubmit(false);
      setLocation("/shopping");
    } else {
      setShowExportPopup(open);
    }
  };
  const handleExportAndRedirect = () => {
    handleExportData();
    setShowExportPopup(false);
    setShowExportAfterSubmit(false);
    setLocation("/shopping");
  };

const handleCategoryChange = (categoryId: string, checked: boolean) => {
  setSelectedCategories(prev =>
    checked
      ? [...prev, categoryId]
      : prev.filter(id => id !== categoryId)
  );
  // Synchronize form's categories field with selectedCategories state
  const currentCategories = form.getValues("categories") || [];
  const newCategories = checked
    ? [...currentCategories, categoryId]
    : currentCategories.filter(id => id !== categoryId);
  form.setValue("categories", newCategories);
};

  const handleExportData = () => {
    const formData = form.getValues();
    const exportData = {
      profile: { ...formData, categories: selectedCategories },
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(exportData, null, 2)], {
      type: 'application/json'
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'shopping-assistant-data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    toast({
      title: "Data Exported",
      description: "Your data has been exported successfully!",
    });
  };

  // On manual submit, show export pop-up
  const onSubmit = async (data: FormData) => {
    // Get latest categories and interests from form state to ensure they are up to date
    const latestCategories = form.getValues("categories") || selectedCategories;
    const latestInterests = form.getValues("interests") || data.interests;

    // Validate categories
    if (!latestCategories || latestCategories.length === 0) {
      setCategoriesError("Please select at least one category");
      if (categoriesRef.current) {
        categoriesRef.current.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      return;
    } else {
      setCategoriesError("");
    }

    const submissionData = {
      ...data,
      categories: latestCategories,
      interests: latestInterests,
    };

    try {
      const currentSessionId = sessionId || createSessionId();
      const response = await apiRequest("POST", "/api/user-info", {
        ...submissionData,
        session_id: currentSessionId,
      }, {
        headers: {
          "X-Session-Id": currentSessionId,
        },
      });
      const result = await response.json();

      if (result.status === "success" && result.session_id) {
        setUserInfo(submissionData);
        setSessionId(result.session_id);
        toast({
          title: "Profile Saved",
          description: "Your information has been saved successfully!",
        });
        setShowExportAfterSubmit(true);
        setShowExportPopup(true);
      } else {
        const newSessionId = createSessionId();
        setUserInfo(submissionData);
        setSessionId(newSessionId);
        toast({
          title: "Profile Saved",
          description: "Your information has been saved successfully! (Session ID generated locally)",
        });
        setShowExportAfterSubmit(true);
        setShowExportPopup(true);
      }
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to save user info",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="py-12 bg-background dark:bg-background min-h-screen">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <Card className="bg-white dark:bg-card rounded-xl shadow-lg border border-gray-100 dark:border-border mb-8">
          <CardHeader className="bg-yellow-400 text-white">
            <CardTitle className="text-2xl font-heading mb-2">Enter User Information</CardTitle>
            <p className="text-white/90 font-body">Help us personalize your shopping experience</p>
          </CardHeader>

          <CardContent className="p-8">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8" noValidate>
                {/* Basic Information */}
                <div className="grid md:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="age"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
                          <Cake className="text-primary mr-2 h-4 w-4" />
                          Age *
                        </FormLabel>
                        <FormControl>
                          <CustomNumberInput
                            value={field.value || 0}
                            setValue={field.onChange}
                            min={1}
                            max={120}
                            step={1}
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                <div className="grid md:grid-cols-2 gap-6">
                  <FormField
                    control={form.control}
                    name="gender"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
                          <Users className="text-primary mr-2 h-4 w-4" />
                          Gender *
                        </FormLabel>
                        <Select onValueChange={field.onChange} value={field.value}>
                          <FormControl>
                            <SelectTrigger className="form-field">
                              <SelectValue placeholder="Select gender" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            <SelectItem value="male">Male</SelectItem>
                            <SelectItem value="female">Female</SelectItem>
                            <SelectItem value="non-binary">Non-binary</SelectItem>
                            <SelectItem value="prefer-not-to-say">Prefer not to say</SelectItem>
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />

                  <FormField
                    control={form.control}
                    name="location"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="flex items-center text-sm font-semibold text-gray-700 dark:text-gray-300">
                          <MapPin className="text-primary mr-2 h-4 w-4" />
                          Location *
                        </FormLabel>
                        <Select onValueChange={(value) => {
                          field.onChange(value);
                          setSelectedCountry(value);
                        }} value={field.value}>
                          <FormControl>
                            <SelectTrigger className="form-field">
                              <SelectValue placeholder="Select your country" />
                            </SelectTrigger>
                          </FormControl>
                          <SelectContent>
                            {countries.map((country) => (
                              <SelectItem key={country.name} value={country.name}>
                                {country.name}
                              </SelectItem>
                            ))}
                          </SelectContent>
                        </Select>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                {/* Shopping Preferences */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-8">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-foreground mb-6 flex items-center">
                    <DollarSign className="text-primary mr-3 h-5 w-5" />
                    Budget Range ({countries.find(c => c.name === selectedCountry)?.currency || "$"}) *
                  </h2>

                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <FormField
                      control={form.control}
                      name="budgetMin"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-sm font-semibold text-gray-700 dark:text-gray-300">Min</FormLabel>
                          <FormControl>
                            <CustomNumberInput
                              value={field.value || 0}
                              setValue={field.onChange}
                              min={0}
                              max={field.value >= form.getValues('budgetMax') ? field.value : form.getValues('budgetMax')}
                              step={1}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />

                    <FormField
                      control={form.control}
                      name="budgetMax"
                      render={({ field }) => (
                        <FormItem>
                          <FormLabel className="text-sm font-semibold text-gray-700 dark:text-gray-300">Max</FormLabel>
                          <FormControl>
                            <CustomNumberInput
                              value={field.value || 0}
                              setValue={field.onChange}
                              min={form.getValues('budgetMin')}
                              max={99999}
                              step={1}
                            />
                          </FormControl>
                          <FormMessage />
                        </FormItem>
                      )}
                    />
                  </div>
                </div>

                {/* Categories */}
                <div ref={categoriesRef} className="border-t border-gray-200 dark:border-gray-700 pt-8">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-foreground mb-6 flex items-center">
                    <ShoppingBag className="text-primary mr-3 h-5 w-5" />
                    Favourite Product Categories *
                  </h3>
                  {(categoriesError || form.formState.errors.categories) && (
                    <div className="text-red-600 dark:text-red-400 font-medium mb-4 animate-shake">
                      {categoriesError || form.formState.errors.categories?.message}
                    </div>
                  )}
                  <div className="grid md:grid-cols-3 gap-3">
                    {categories.map((category) => (
                      <div key={category.id} className="flex items-center space-x-2">
                        <Checkbox
                          id={category.id}
                          checked={selectedCategories.includes(category.id)}
                          onCheckedChange={(checked) =>
                            handleCategoryChange(category.id, checked as boolean)
                          }
                          className="text-primary"
                        />
                        <label
                          htmlFor={category.id}
                          className="text-sm text-gray-700 dark:text-gray-300 cursor-pointer"
                        >
                          {category.label}
                        </label>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Interests */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-8">
                  <FormField
                    control={form.control}
                    name="interests"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel className="text-xl font-semibold text-gray-900 dark:text-foreground mb-4 flex items-center">
                          <User className="text-primary mr-3 h-5 w-5" />
                          Interests and Hobbies *
                        </FormLabel>
                        <FormControl>
                          <Textarea
                            {...field}
                            rows={4}
                            placeholder="Tell us about your interests, hobbies, and what you're passionate about..."
                            className="form-field"
                          />
                        </FormControl>
                        <FormMessage />
                      </FormItem>
                    )}
                  />
                </div>

                {/* Data Management */}
                <div className="border-t border-gray-200 dark:border-gray-700 pt-8">
                  <h3 className="text-xl font-semibold text-gray-900 dark:text-foreground mb-6 flex items-center">
                    <Database className="text-primary mr-3 h-5 w-5" />
                    Data Management
                  </h3>
                  <div className="flex flex-wrap gap-4">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleImportData}
                      className="border-primary text-primary hover:bg-primary/10"
                    >
                      <Upload className="mr-2 h-4 w-4" />
                      Import Data
                    </Button>
                    <Button
                      type="button"
                      variant="outline"
                      onClick={handleExportData}
                      className="border-primary text-primary hover:bg-primary/10"
                    >
                      <Download className="mr-2 h-4 w-4" />
                      Export Data
                    </Button>
                  </div>
                </div>

                {/* Form Actions */}
                <div className="flex justify-between items-center pt-8 border-t border-gray-200 dark:border-gray-700">
                  <Button
                    type="button"
                    variant="ghost"
                    onClick={() => setLocation('/')}
                    className="text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200"
                  >
                    <ArrowLeft className="mr-2 h-4 w-4" />
                    Back
                  </Button>
                  <Button
                    type="submit"
                    className="btn-primary bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    Continue to Shopping
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </form>
            </Form>
          </CardContent>
        </Card>
      </div>
      <AlertDialog open={showExportPopup} onOpenChange={handleExportPopupChange}>
        <AlertDialogContent className="animate-fade-in">
          <button
            className="absolute top-2 right-2 text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 transition-colors"
            onClick={() => handleExportPopupChange(false)}
            aria-label="Close"
            type="button"
          >
            <X className="w-5 h-5" />
          </button>
          <AlertDialogHeader>
            <AlertDialogTitle>Export Your User Info</AlertDialogTitle>
            <AlertDialogDescription>
              Export your user info to make it easier to add next time!
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogAction onClick={handleExportAndRedirect} className="w-full mt-4">
            Export Now
          </AlertDialogAction>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
