# ?? **COMPREHENSIVE CODEBASE CLEANUP - ACTION PLAN**

## ?? **ANALYSIS RESULTS**

### **?? Critical Issues Found:**
1. **Legacy method still exists**: `_force_coordinate_system_refresh` in canvas_widget.py
2. **Canvas widget still too large**: 865 lines (should be ? 600)
3. **Too many debug prints**: 34+ debug print statements
4. **Old attributes still present**: 15 legacy attributes found

### **? Major Opportunities:**
1. **Code duplication**: Multiple duplicate logic patterns
2. **Deep nesting**: Complex conditional structures  
3. **Architecture violations**: Canvas doing manager responsibilities
4. **Magic numbers**: Hardcoded values throughout code

---

## ?? **CLEANUP EXECUTION PLAN**

### **Phase 1: Remove Critical Legacy Code** ??
1. ? Remove `_force_coordinate_system_refresh` method
2. ? Clean up remaining debug prints
3. ? Remove old attributes from canvas
4. ? Fix deprecated import references

### **Phase 2: Simplify Canvas Widget** ??
1. ? Extract remaining complex methods to managers
2. ? Reduce canvas widget to ? 600 lines
3. ? Ensure pure delegation pattern

### **Phase 3: Eliminate Code Duplication** ??
1. ? Extract common coordinate logic
2. ? Create shared measurement utilities
3. ? Consolidate similar methods

### **Phase 4: Improve Code Quality** ?
1. ? Replace magic numbers with constants
2. ? Simplify complex conditionals
3. ? Reduce method complexity

---

## ?? **EXPECTED OUTCOMES**

- **Zero legacy code** - No old methods or attributes
- **Simplified architecture** - Canvas ? 600 lines
- **Clean separation** - Perfect delegation pattern
- **High maintainability** - Easy to understand and modify
- **Production ready** - Professional code quality

**Let's execute this plan step by step!**