import { Linkedin, Github, Globe } from "@/lib/icons";

export default function Footer() {
  return (
    <footer className="bg-background dark:bg-background py-8 border-t border-gray-200 dark:border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center">
          <h2 className="font-semibold mb-4 text-2xl text-gray-900 dark:text-foreground">Connect With Us</h2>
          <div className="flex space-x-8">
            <a href="https://www.linkedin.com/in/bharath-sadineni-9b1304174/" target="_blank" rel="noopener noreferrer" className="flex flex-col items-center group">
              <Linkedin className="h-8 w-8 text-primary group-hover:text-blue-700 transition-colors" />
              <span className="text-xs mt-1 text-gray-600 dark:text-muted-foreground">LinkedIn</span>
            </a>
            <a href="https://github.com/BharathSadineni" target="_blank" rel="noopener noreferrer" className="flex flex-col items-center group">
              <Github className="h-8 w-8 text-primary group-hover:text-black dark:group-hover:text-white transition-colors" />
              <span className="text-xs mt-1 text-gray-600 dark:text-muted-foreground">GitHub</span>
            </a>
            <a href="https://bharathsadineni.github.io/BharathSadineni/" target="_blank" rel="noopener noreferrer" className="flex flex-col items-center group">
              <Globe className="h-8 w-8 text-primary group-hover:text-green-600 transition-colors" />
              <span className="text-xs mt-1 text-gray-600 dark:text-muted-foreground">Portfolio</span>
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
