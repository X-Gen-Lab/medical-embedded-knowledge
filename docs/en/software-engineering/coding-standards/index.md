---
title: "Coding Standards"
description: "Coding standards for medical device embedded software, including MISRA C, CERT C, and code review checklists"
difficulty: "Intermediate"
estimated_time: "4 hours"
tags: ["Coding Standards", "MISRA C", "CERT C", "Code Quality"]
related_modules:
  - "technical-knowledge/embedded-c-cpp"
  - "software-engineering/static-analysis"
  - "regulatory-standards/iec-62304"
last_updated: "2026-02-07"
version: "1.0"
language: "en-US"
translation_status: complete
---

# Coding Standards

## Learning Objectives

After completing this module, you will be able to:
- Understand the importance of coding standards in medical device software
- Master core rules of MISRA C and CERT C
- Apply coding standards to actual development
- Conduct effective code reviews
- Use static analysis tools to enforce coding standards

## Prerequisites

- C/C++ programming fundamentals
- Embedded systems basics
- Understanding of software quality concepts

## Why Coding Standards Matter

In medical device software development, coding standards are crucial for:

1. **Safety**: Prevent common programming errors that could lead to system failures
2. **Reliability**: Improve code quality and reduce defects
3. **Maintainability**: Make code easier to understand and modify
4. **Compliance**: Meet regulatory requirements (IEC 62304, FDA, etc.)
5. **Consistency**: Ensure uniform code style across the team

!!! warning "Regulatory Requirements"
    IEC 62304 requires Class B and C software to follow established coding standards. MISRA C and CERT C are widely accepted standards in the medical device industry.

## Main Coding Standards

### MISRA C

**MISRA** (Motor Industry Software Reliability Association) C is a set of software development guidelines for the C programming language, originally developed for the automotive industry but widely adopted in medical devices.

**Key Features**:
- 143 rules (MISRA C:2012)
- Divided into mandatory, required, and advisory rules
- Focus on avoiding undefined behavior and implementation-defined behavior
- Emphasize code clarity and maintainability

**Rule Categories**:
1. **Mandatory**: Must be followed, no deviations allowed
2. **Required**: Should be followed, deviations require justification
3. **Advisory**: Recommended, deviations allowed

**Example Rules**:
- Rule 1.3: No undefined or critical unspecified behavior
- Rule 2.1: No unreachable code
- Rule 8.13: Pointer parameters should be const if not modified
- Rule 21.3: malloc and free shall not be used

[Learn more about MISRA C](misra-c.md)

### CERT C

**CERT C** is a secure coding standard developed by the CERT Coordination Center at Carnegie Mellon University, focusing on security vulnerabilities.

**Key Features**:
- Focus on security vulnerabilities
- Covers common attack vectors
- Provides specific recommendations and examples
- Complementary to MISRA C

**Rule Categories**:
1. **Preprocessor (PRE)**
2. **Declarations and Initialization (DCL)**
3. **Expressions (EXP)**
4. **Integers (INT)**
5. **Floating Point (FLP)**
6. **Arrays (ARR)**
7. **Characters and Strings (STR)**
8. **Memory Management (MEM)**
9. **Input/Output (FIO)**
10. **Environment (ENV)**
11. **Signals (SIG)**
12. **Error Handling (ERR)**
13. **Concurrency (CON)**

[Learn more about CERT C](cert-c.md)

## Code Review Process

### Code Review Checklist

**Functionality**:
- [ ] Does the code implement the requirements correctly?
- [ ] Are all edge cases handled?
- [ ] Is error handling appropriate?

**Coding Standards**:
- [ ] Does the code follow MISRA C/CERT C rules?
- [ ] Are naming conventions consistent?
- [ ] Is code formatting consistent?

**Safety and Security**:
- [ ] Are there buffer overflow risks?
- [ ] Are all inputs validated?
- [ ] Are resources properly released?

**Performance**:
- [ ] Are there obvious performance issues?
- [ ] Is memory usage reasonable?
- [ ] Are algorithms efficient?

**Maintainability**:
- [ ] Is the code easy to understand?
- [ ] Are comments adequate and accurate?
- [ ] Is the code structure clear?

[View complete code review checklist](code-review-checklist.md)

## Static Analysis Tools

Static analysis tools automatically check code for compliance with coding standards:

**Common Tools**:
1. **PC-lint/FlexeLint**: Comprehensive C/C++ static analyzer
2. **Coverity**: Enterprise-level static analysis platform
3. **Klocwork**: Static analysis and code review tool
4. **Polyspace**: MATLAB-based static analysis tool
5. **Cppcheck**: Open-source C/C++ static analyzer

**Tool Usage Best Practices**:
- Integrate into CI/CD pipeline
- Configure appropriate rule sets
- Regularly review and address findings
- Document justified deviations
- Track metrics over time

## Best Practices

!!! tip "Coding Best Practices"
    1. **Follow Standards Consistently**: Apply coding standards to all code
    2. **Automate Checking**: Use static analysis tools for automated enforcement
    3. **Document Deviations**: All deviations from standards must be documented and justified
    4. **Regular Reviews**: Conduct regular code reviews
    5. **Continuous Improvement**: Update standards based on lessons learned

## Common Pitfalls

!!! warning "Common Mistakes"
    1. **Ignoring Warnings**: Treating compiler warnings as non-critical
    2. **Inconsistent Application**: Applying standards only to new code
    3. **Over-reliance on Tools**: Tools cannot catch all issues
    4. **Lack of Training**: Team members not understanding the rationale behind rules
    5. **No Deviation Process**: Allowing undocumented deviations

## Practice Exercises

1. Review a code sample and identify MISRA C violations
2. Configure a static analysis tool for your project
3. Create a code review checklist for your team
4. Refactor code to comply with MISRA C rules

## Self-Assessment Questions

??? question "Question 1: What are the three categories of MISRA C rules?"
    
    ??? success "Answer"
        MISRA C rules are categorized into three types:
        
        1. **Mandatory**: Must be followed without exception. No deviations allowed.
        2. **Required**: Should be followed. Deviations require formal justification and documentation.
        3. **Advisory**: Recommended but not required. Deviations are acceptable.
        
        The categorization helps teams prioritize compliance efforts and manage deviations appropriately.

??? question "Question 2: Why does MISRA C prohibit the use of malloc and free?"
    
    ??? success "Answer"
        MISRA C Rule 21.3 prohibits malloc and free because:
        
        1. **Non-determinism**: Allocation time is unpredictable
        2. **Memory Fragmentation**: Can lead to allocation failures over time
        3. **Memory Leaks**: Easy to forget to free allocated memory
        4. **Safety Concerns**: Difficult to prove absence of memory-related defects
        
        **Alternatives**:
        - Use static allocation
        - Use memory pools with fixed-size blocks
        - Pre-allocate all required memory at initialization
        
        These alternatives provide deterministic behavior required for safety-critical systems.

## Related Resources

- [MISRA C Details](misra-c.md)
- [CERT C Details](cert-c.md)
- [Code Review Checklist](code-review-checklist.md)
- [Static Analysis](../static-analysis/index.md)
- [Embedded C/C++](../../technical-knowledge/embedded-c-cpp/index.md)

## References

1. MISRA C:2012 - Guidelines for the use of the C language in critical systems
2. SEI CERT C Coding Standard - Rules for Developing Safe, Reliable, and Secure Systems
3. IEC 62304:2006+AMD1:2015 - Medical device software lifecycle processes
4. "Embedded C Coding Standard" by Michael Barr
5. ISO/IEC 9899:2018 - Programming languages - C
