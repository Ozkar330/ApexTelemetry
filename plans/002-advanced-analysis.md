# Plan: Advanced F1 Data Analysis

This plan outlines the implementation of tire degradation analysis and a comprehensive lap time table.

## Goal

Provide structured data for every driver's lap times and analyze how tire age affects performance across different compounds.

## Proposed Changes

### 1. Simple Lap Time Table (`src/analysis.py`)
- Create a function to generate a clean, filtered lap time table.
- Support pivoting data: Rows as `LapNo`, Columns as `Driver`.
- Support filtering by driver list and lap range.

### 2. Tire Degradation Analysis (`src/analysis.py`)
- Create a function to analyze lap time trends relative to `TyreAge` and `Compound`.
- Filter out "dirty" laps:
    - Laps with `TrackStatus` != '1' (to exclude SC, VSC, Yellow flags).
    - Laps with `PitIn` or `PitOut` (to exclude pit stop influence).
- Group by `Compound` and `TyreAge` to calculate mean/median lap times.

## Verification Plan

### Automated Tests
- Add `tests/test_analysis.py` to verify:
    - Lap time table dimensions and values.
    - Tire degradation grouping logic.
    - Filter effectiveness.

### Manual Verification
- Run `python src/analysis.py` and inspect the output tables for consistency.
