# Week 1: Function Fundamentals - Complete Learning Guide

## Day 1-2: Basic Function Design Patterns

### 1. Function Signature Best Practices

def calculate_total(price, tax_rate=0.08, discount=0, currency="USD"):
    """
    Calculate total price with tax and discount.
    
    Args:
        price (float): Base price
        tax_rate (float): Tax rate (default: 0.08)
        discount (float): Discount amount (default: 0)
        currency (str): Currency code (default: "USD")
    
    Returns:
        dict: Contains total, breakdown, and currency
    """
    subtotal = price - discount
    tax_amount = subtotal * tax_rate
    total = subtotal + tax_amount
    
    return {
        'total': round(total, 2),
        'subtotal': round(subtotal, 2),
        'tax': round(tax_amount, 2),
        'currency': currency
    }

# Example usage
result = calculate_total(100, tax_rate=0.1, discount=10)
print(result)


### 2. Single Responsibility Functions

# Bad: Function doing too many things
def process_user_data_bad(user_data):
    # Validate
    if not user_data.get('email'):
        raise ValueError("Email required")
    
    # Transform
    user_data['email'] = user_data['email'].lower()
    user_data['name'] = user_data['name'].title()
    
    # Save to database (mock)
    print(f"Saving {user_data} to database")
    
    # Send email (mock)
    print(f"Sending welcome email to {user_data['email']}")

# Good: Separate concerns
def validate_user_data(user_data):
    """Validate user data structure."""
    if not user_data.get('email'):
        raise ValueError("Email required")
    if not user_data.get('name'):
        raise ValueError("Name required")
    return True

def normalize_user_data(user_data):
    """Normalize user data format."""
    normalized = user_data.copy()
    normalized['email'] = normalized['email'].lower().strip()
    normalized['name'] = normalized['name'].title().strip()
    return normalized

def save_user(user_data):
    """Save user to database."""
    print(f"Saving {user_data} to database")
    return True

def send_welcome_email(email):
    """Send welcome email to user."""
    print(f"Sending welcome email to {email}")
    return True

def process_user_data_good(user_data):
    """Process user data through validation, normalization, and actions."""
    validate_user_data(user_data)
    normalized_data = normalize_user_data(user_data)
    save_user(normalized_data)
    send_welcome_email(normalized_data['email'])
    return normalized_data


## Day 3-4: *args and **kwargs Mastery

### 1. Understanding *args (Variable Positional Arguments)

def sum_all(*numbers):
    """Sum any number of arguments."""
    return sum(numbers)

def create_full_name(*name_parts):
    """Create full name from any number of name parts."""
    return ' '.join(str(part).title() for part in name_parts if part)

# Examples
print(sum_all(1, 2, 3, 4, 5))  # 15
print(create_full_name("john", "michael", "doe"))  # John Michael Doe

# Advanced: Combining with regular parameters
def log_message(level, *messages, timestamp=None):
    """Log messages with a specific level."""
    import datetime
    ts = timestamp or datetime.datetime.now().isoformat()
    combined_message = ' '.join(str(msg) for msg in messages)
    print(f"[{ts}] {level.upper()}: {combined_message}")

log_message("info", "User", "logged", "in", "successfully")


### 2. Understanding **kwargs (Variable Keyword Arguments)

def create_user(**user_info):
    """Create user with flexible attributes."""
    required_fields = {'name', 'email'}
    provided_fields = set(user_info.keys())
    
    if not required_fields.issubset(provided_fields):
        missing = required_fields - provided_fields
        raise ValueError(f"Missing required fields: {missing}")
    
    # Set defaults for optional fields
    defaults = {
        'active': True,
        'role': 'user',
        'created_at': None
    }
    
    for key, default_value in defaults.items():
        user_info.setdefault(key, default_value)
    
    return user_info

# Usage examples
user1 = create_user(name="Alice", email="alice@example.com")
user2 = create_user(
    name="Bob", 
    email="bob@example.com", 
    role="admin", 
    department="IT",
    employee_id=12345
)

print(user1)
print(user2)


### 3. Combining *args and **kwargs

def flexible_api_call(endpoint, *path_parts, method="GET", **params):
    """Simulate flexible API call with various parameters."""
    # Build URL
    url_parts = [endpoint.rstrip('/')]
    url_parts.extend(str(part) for part in path_parts)
    full_url = '/'.join(url_parts)
    
    # Build query string
    query_params = '&'.join(f"{k}={v}" for k, v in params.items() if v is not None)
    if query_params:
        full_url += f"?{query_params}"
    
    return {
        'method': method,
        'url': full_url,
        'params': params
    }

# Usage examples
api1 = flexible_api_call("https://api.example.com", "users", method="GET")
api2 = flexible_api_call("https://api.example.com", "users", 123, "posts", 
                        method="GET", limit=10, offset=20, include_meta=True)

print(api1)
print(api2)


### 4. Function Argument Unpacking

def calculate_rectangle_area(length, width, unit="sq ft"):
    """Calculate rectangle area."""
    area = length * width
    return f"{area} {unit}"

# Unpacking examples
dimensions = (10, 5)
print(calculate_rectangle_area(*dimensions))

room_info = {'length': 12, 'width': 8, 'unit': 'sq meters'}
print(calculate_rectangle_area(**room_info))

# Mixed unpacking
args = (15, 10)
kwargs = {'unit': 'sq inches'}
print(calculate_rectangle_area(*args, **kwargs))


## Day 5-7: Configuration Parser Project

class ConfigurationParser:
    """
    Flexible configuration parser that accepts various parameter formats.
    Supports: dict, keyword arguments, file paths, and mixed formats.
    """
    
    def __init__(self, **default_config):
        """Initialize with default configuration."""
        self.config = default_config.copy()
        self.validators = {}
        self.transformers = {}
    
    def add_validator(self, key, validator_func):
        """Add validation function for specific config key."""
        self.validators[key] = validator_func
    
    def add_transformer(self, key, transformer_func):
        """Add transformation function for specific config key."""
        self.transformers[key] = transformer_func
    
    def parse(self, *sources, **overrides):
        """
        Parse configuration from multiple sources.
        
        Args:
            *sources: Can be dicts, file paths, or other config objects
            **overrides: Direct key-value overrides
        
        Returns:
            dict: Merged and validated configuration
        """
        # Start with current config
        result = self.config.copy()
        
        # Process each source
        for source in sources:
            if isinstance(source, dict):
                result.update(source)
            elif isinstance(source, str):
                # Assume it's a file path
                file_config = self._load_from_file(source)
                result.update(file_config)
            elif hasattr(source, 'to_dict'):
                # Custom config object with to_dict method
                result.update(source.to_dict())
            else:
                raise ValueError(f"Unsupported config source type: {type(source)}")
        
        # Apply overrides
        result.update(overrides)
        
        # Apply transformations
        for key, value in result.items():
            if key in self.transformers:
                result[key] = self.transformers[key](value)
        
        # Validate
        self._validate_config(result)
        
        return result
    
    def _load_from_file(self, file_path):
        """Load configuration from file (supports JSON, YAML-like simple format)."""
        import json
        
        try:
            with open(file_path, 'r') as f:
                if file_path.endswith('.json'):
                    return json.load(f)
                else:
                    # Simple key=value format
                    config = {}
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            if '=' in line:
                                key, value = line.split('=', 1)
                                # Try to convert to appropriate type
                                config[key.strip()] = self._convert_value(value.strip())
                    return config
        except FileNotFoundError:
            print(f"Warning: Config file {file_path} not found. Skipping.")
            return {}
        except Exception as e:
            print(f"Error loading config from {file_path}: {e}")
            return {}
    
    def _convert_value(self, value_str):
        """Convert string value to appropriate Python type."""
        # Remove quotes
        value_str = value_str.strip('\'"')
        
        # Boolean conversion
        if value_str.lower() in ('true', 'yes', 'on'):
            return True
        elif value_str.lower() in ('false', 'no', 'off'):
            return False
        
        # Number conversion
        try:
            if '.' in value_str:
                return float(value_str)
            else:
                return int(value_str)
        except ValueError:
            pass
        
        # Return as string if no conversion possible
        return value_str
    
    def _validate_config(self, config):
        """Validate configuration using registered validators."""
        for key, validator in self.validators.items():
            if key in config:
                if not validator(config[key]):
                    raise ValueError(f"Validation failed for config key '{key}': {config[key]}")


# Example Usage and Testing

if __name__ == "__main__":
    # Create parser with defaults
    parser = ConfigurationParser(
        debug=False,
        port=8000,
        host="localhost",
        max_connections=100
    )
    
    # Add validators
    parser.add_validator('port', lambda x: isinstance(x, int) and 1 <= x <= 65535)
    parser.add_validator('max_connections', lambda x: isinstance(x, int) and x > 0)
    
    # Add transformers
    parser.add_transformer('host', lambda x: x.lower().strip())
    
    # Test 1: Parse from dictionary
    config1 = parser.parse({'debug': True, 'port': 3000})
    print("Config 1 (from dict):", config1)
    
    # Test 2: Parse with keyword arguments
    config2 = parser.parse(debug=True, host="0.0.0.0", new_setting="value")
    print("Config 2 (from kwargs):", config2)
    
    # Test 3: Parse from multiple sources
    db_config = {'database_url': 'postgresql://localhost/mydb', 'pool_size': 10}
    config3 = parser.parse(
        db_config,
        port=5000,
        debug=True
    )
    print("Config 3 (mixed sources):", config3)
    
    # Test 4: Create and parse from file
    sample_config_content = """# Sample configuration
debug=true
port=9000
host=0.0.0.0
max_connections=500
api_key=secret123
"""
    
    # Write sample config file
    with open('sample_config.txt', 'w') as f:
        f.write(sample_config_content)
    
    # Parse from file
    config4 = parser.parse('sample_config.txt', debug=False)
    print("Config 4 (from file + override):", config4)
    
    # Cleanup
    import os
    try:
        os.remove('sample_config.txt')
    except:
        pass


## Practice Exercises

# Exercise 1: Rewrite this inflexible function
def calculate_shipping_old(weight, distance, express=False):
    base_rate = 5.0
    per_kg = 2.0
    per_km = 0.1
    express_multiplier = 2.0
    
    cost = base_rate + (weight * per_kg) + (distance * per_km)
    if express:
        cost *= express_multiplier
    return cost

# Your task: Rewrite using *args, **kwargs to accept:
# - Multiple packages (weights)
# - Various shipping options
# - Different rate structures
# - Custom multipliers

def calculate_shipping_flexible(*packages, **options):
    """
    YOUR IMPLEMENTATION HERE
    Should handle:
    - Multiple package weights: calculate_shipping_flexible(2.5, 1.2, 3.0)
    - Options: express=True, insurance=True, rate_per_kg=2.5
    - Custom rates: base_rate=10, distance_rate=0.2
    """
    pass  # Implement this!


# Exercise 2: Create a flexible data processor
def process_data_flexible(*data_sources, output_format="dict", **processing_options):
    """
    Create a function that can:
    - Accept multiple data sources (lists, dicts, file paths)
    - Process with various options (sort, filter, transform)
    - Return in different formats
    
    Example usage:
    process_data_flexible([1,2,3], {'a': 1}, sort=True, filter_func=lambda x: x > 1)
    """
    pass  # Your implementation


# Exercise 3: Build a flexible API client
class FlexibleAPIClient:
    """
    Build a class that can make API calls with:
    - Various HTTP methods
    - Different authentication methods
    - Flexible parameter passing
    - Custom headers and options
    """
    
    def __init__(self, base_url, **default_options):
        # Your implementation
        pass
    
    def request(self, endpoint, *path_parts, method="GET", **options):
        # Your implementation
        pass


## Key Takeaways for Week 1

"""
1. Function Design Principles:
   - Single responsibility
   - Clear parameter naming
   - Appropriate defaults
   - Comprehensive docstrings

2. *args Usage:
   - For functions accepting variable positional arguments
   - Useful for mathematical operations, logging, string operations
   - Can be combined with regular parameters

3. **kwargs Usage:
   - For functions accepting variable keyword arguments
   - Great for configuration, optional parameters, API wrappers
   - Enables flexible interfaces

4. Best Practices:
   - Use *args and **kwargs judiciously - don't overuse
   - Always document what your function accepts
   - Validate inputs when using flexible parameters
   - Consider type hints for better code documentation

5. Real-world Applications:
   - Configuration systems
   - API wrappers
   - Data processing pipelines
   - Plugin architectures
"""