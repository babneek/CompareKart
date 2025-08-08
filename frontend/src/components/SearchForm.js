import React, { useState, useEffect } from 'react';
import { Search, ChevronDown, Check, X } from 'lucide-react';
import { apiService } from '../services/api';
import toast from 'react-hot-toast';

const SearchForm = ({ onSearch, isLoading }) => {
  const [product, setProduct] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState([]);
  const [categories, setCategories] = useState({});
  const [platforms, setPlatforms] = useState([]);
  const [showCategoryDropdown, setShowCategoryDropdown] = useState(false);
  const [showPlatformDropdown, setShowPlatformDropdown] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(true);

  // Load categories and platforms on component mount
  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoadingData(true);
        const [categoriesData, platformsData] = await Promise.all([
          apiService.getCategories(),
          apiService.getPlatforms()
        ]);
        
        setCategories(categoriesData.categories || {});
        setPlatforms(platformsData.platforms || []);
      } catch (error) {
        console.error('Error loading data:', error);
        toast.error('Failed to load platform data');
      } finally {
        setIsLoadingData(false);
      }
    };

    loadData();
  }, []);

  // Update selected platforms when category changes
  useEffect(() => {
    if (selectedCategory && categories[selectedCategory]) {
      const categoryPlatforms = categories[selectedCategory].platforms;
      setSelectedPlatforms(categoryPlatforms);
    }
  }, [selectedCategory, categories]);

  const handleCategorySelect = (categoryId) => {
    setSelectedCategory(categoryId);
    setShowCategoryDropdown(false);
  };

  const handlePlatformToggle = (platformId) => {
    setSelectedPlatforms(prev => {
      if (prev.includes(platformId)) {
        return prev.filter(p => p !== platformId);
      } else {
        return [...prev, platformId];
      }
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!product.trim()) {
      toast.error('Please enter a product name');
      return;
    }

    if (selectedPlatforms.length === 0) {
      toast.error('Please select at least one platform');
      return;
    }

    onSearch({
      product: product.trim(),
      category: selectedCategory || null,
      platforms: selectedPlatforms,
      maxResults: 5
    });
  };

  const clearFilters = () => {
    setSelectedCategory('');
    setSelectedPlatforms([]);
    setShowCategoryDropdown(false);
    setShowPlatformDropdown(false);
  };

  const getSelectedCategoryName = () => {
    if (!selectedCategory || !categories[selectedCategory]) return 'All Categories';
    return categories[selectedCategory].name;
  };

  const getSelectedPlatformsText = () => {
    if (selectedPlatforms.length === 0) return 'Select Platforms';
    if (selectedPlatforms.length === 1) {
      const platform = platforms.find(p => p.id === selectedPlatforms[0]);
      return platform ? platform.name : selectedPlatforms[0];
    }
    return `${selectedPlatforms.length} platforms selected`;
  };

  if (isLoadingData) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8 mb-8 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-12 bg-gray-200 rounded mb-4"></div>
        <div className="flex gap-4">
          <div className="h-12 bg-gray-200 rounded flex-1"></div>
          <div className="h-12 bg-gray-200 rounded flex-1"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
      <h2 className="text-2xl font-bold text-gray-800 mb-6 text-center">
        🛍️ Smart Price Comparison
      </h2>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Category Selection */}
        <div className="relative">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowCategoryDropdown(!showCategoryDropdown)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-left flex items-center justify-between hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <span className="flex items-center">
                {selectedCategory && categories[selectedCategory] && (
                  <span className="mr-2">{categories[selectedCategory].icon}</span>
                )}
                {getSelectedCategoryName()}
              </span>
              <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ${showCategoryDropdown ? 'rotate-180' : ''}`} />
            </button>
            
            {showCategoryDropdown && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                <button
                  type="button"
                  onClick={() => handleCategorySelect('')}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center"
                >
                  <span className="mr-2">🛒</span>
                  All Categories
                </button>
                {Object.entries(categories).map(([categoryId, category]) => (
                  <button
                    key={categoryId}
                    type="button"
                    onClick={() => handleCategorySelect(categoryId)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <span className="mr-2">{category.icon}</span>
                      <div>
                        <div className="font-medium">{category.name}</div>
                        <div className="text-sm text-gray-500">{category.description}</div>
                      </div>
                    </div>
                    {selectedCategory === categoryId && (
                      <Check className="h-5 w-5 text-blue-500" />
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Platform Selection */}
        <div className="relative">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Platforms
          </label>
          <div className="relative">
            <button
              type="button"
              onClick={() => setShowPlatformDropdown(!showPlatformDropdown)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-white text-left flex items-center justify-between hover:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <span>{getSelectedPlatformsText()}</span>
              <ChevronDown className={`h-5 w-5 text-gray-400 transition-transform ${showPlatformDropdown ? 'rotate-180' : ''}`} />
            </button>
            
            {showPlatformDropdown && (
              <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                {platforms.map((platform) => (
                  <button
                    key={platform.id}
                    type="button"
                    onClick={() => handlePlatformToggle(platform.id)}
                    className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center justify-between"
                  >
                    <div className="flex items-center">
                      <div className="flex flex-wrap gap-1 mr-3">
                        {platform.categories.map(cat => (
                          <span key={cat.id} className="text-xs">{cat.icon}</span>
                        ))}
                      </div>
                      <span className="font-medium">{platform.name}</span>
                    </div>
                    <div className="flex items-center">
                      {selectedPlatforms.includes(platform.id) && (
                        <Check className="h-5 w-5 text-blue-500" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Product Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Product Name
          </label>
          <div className="relative">
            <input
              type="text"
              value={product}
              onChange={(e) => setProduct(e.target.value)}
              placeholder="e.g., iPhone 15 Pro Max, Nike Air Max, Samsung TV..."
              className="w-full px-4 py-3 pl-12 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              disabled={isLoading}
            />
            <Search className="absolute left-4 top-3.5 h-5 w-5 text-gray-400" />
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4">
          <button
            type="submit"
            disabled={isLoading || selectedPlatforms.length === 0}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed font-medium transition-colors"
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Searching...
              </div>
            ) : (
              <div className="flex items-center justify-center">
                <Search className="h-5 w-5 mr-2" />
                Compare Prices
              </div>
            )}
          </button>
          
          {(selectedCategory || selectedPlatforms.length > 0) && (
            <button
              type="button"
              onClick={clearFilters}
              className="px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 font-medium transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          )}
        </div>

        {/* Selected Filters Display */}
        {(selectedCategory || selectedPlatforms.length > 0) && (
          <div className="flex flex-wrap gap-2 pt-2">
            {selectedCategory && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800">
                {categories[selectedCategory]?.icon} {categories[selectedCategory]?.name}
              </span>
            )}
            {selectedPlatforms.map(platformId => {
              const platform = platforms.find(p => p.id === platformId);
              return platform ? (
                <span key={platformId} className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-800">
                  {platform.name}
                </span>
              ) : null;
            })}
          </div>
        )}
      </form>
    </div>
  );
};

export default SearchForm;
