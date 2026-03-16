# 🚧 Pipeline Profile Optimization using Linear Programming

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Optimization](https://img.shields.io/badge/Optimization-PuLP-orange)
![Visualization](https://img.shields.io/badge/Visualization-Matplotlib-green)

This repository contains a suite of Python scripts that utilize the `pulp` linear programming library to solve a complex civil engineering earthworks problem. 

The objective of this case study is to determine the most cost-effective vertical alignment for a 1,400-meter pipeline stretch by minimizing the costs associated with cutting, filling, borrowing, and dumping soil, while strictly adhering to maximum grade and boundary constraints.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Repository Structure & Solutions](#repository-structure--solutions)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Key Linear Programming Concepts](#key-linear-programming-concepts)

---

## 📖 Project Overview

When routing a pipeline over hilly terrain, massive costs are incurred by moving earth to maintain safe pipe angles. This project models the terrain as a mathematical optimization problem. 
* **Objective:** Minimize total earthworks cost (Cut: ₹150, Fill: ₹100, Dump: ₹70, Borrow: ₹120).
* **Constraints:** Maintain fixed boundary elevations, adhere to incoming/outgoing slopes, ensure the pipeline never exceeds an 8% grade, and ensure the pipeline bend never exceeds a 10% change in grade.

---

## 📂 Repository Structure & Solutions

This project is broken down into four distinct analytical scripts:

### `01_base_optimization.py` 
**The Baseline Model:** Calculates the absolute minimum earthwork cost to complete the project. Applies cost-saving measures such as reducing the Right-of-Way (RoW) working width to 10 meters and relaxing strict grade limits to reflect realistic pipeline engineering standards.

### `02_alternative_optima.py` 
**Alternative Solutions Search:** Uses *Objective Bounding* to prove that multiple distinct elevation profiles can yield the exact same minimum total cost. It locks in the lowest budget and maximizes elevation at a specific station to generate an alternative physical profile.

### `03_bottleneck_relaxation.py` 
**0.5% Grade Relaxation Analysis:** Analyzes the LP *Shadow Prices (Dual Values)* to identify the single most restrictive 100-meter segment of the pipeline. It then dynamically relaxes that segment's maximum grade limit by 0.5% to prove the maximum possible cost savings.

### `04_boundary_analysis.py` 
**System Extension Analysis:** Evaluates whether the optimization model should be extended beyond the current 1,400m stretch. It isolates the boundary constraints and checks their Shadow Prices to determine if the fixed connection points are acting as expensive, artificial bottlenecks.
---

## ⚙️ Installation & Setup

To run these scripts locally, you will need Python installed on your machine.

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/your-username/pipeline-optimization.git](https://github.com/your-username/pipeline-optimization.git)
   cd pipeline-optimization
