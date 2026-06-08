# SOURCE_CODE_FIRST renderer for Phase49 enhanced Fig2.
#
# PERSIST_SOURCE_CODE_FIRST_PROTOCOL:
# - VISUAL_REFERENCES: user-requested raincloud, ComplexHeatmap, radial
#   lollipop, and reviewer-facing stability decision quadrant.
# - SOURCE_CODE_SNAPSHOT: R-native ComplexHeatmap and grid decision-plot
#   grammar are bound to original project CSVs; no simulated data are used.
# - PORTING_PROMPT: ComplexHeatmap is used only for the method-agreement matrix;
#   do not simulate or substitute visual-only data.

suppressPackageStartupMessages({
  library(grid)
})

root <- "/mnt/e/Reserch/Older women"
pkg <- file.path(root, "manuscript/bmc_geriatrics_submission_burden_profiles_rescue")
redraw <- file.path(root, "figure_redraw/phase49_fig1_3_enhanced_visual_power")
out_dir <- file.path(redraw, "outputs")
tab_dir <- file.path(redraw, "intermediate_tables")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(tab_dir, recursive = TRUE, showWarnings = FALSE)

required <- c("ComplexHeatmap", "circlize")
missing <- required[!vapply(required, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing) > 0) {
  stop("Missing required R package(s) for requested ComplexHeatmap panel: ", paste(missing, collapse = ", "))
}
suppressPackageStartupMessages({
  library(ComplexHeatmap)
  library(circlize)
})

cohort_order <- c("CHARLS", "ELSA", "HRS", "KLoSA", "LASI", "MHAS", "SHARE")
method_order <- c("gmm_diag", "gmm_tied", "kmeans", "hierarchical_ward_sample", "continuous_severity_tertile")
method_labels <- c("diag\nGMM", "tied\nGMM", "k-means", "Ward", "severity\ntertile")
tier_colors <- c(
  "Strict-core" = "#176C73",
  "Functional bridge sensitivity" = "#D08B1E",
  "Baseline-only descriptive" = "#91979C",
  "Validation-downgraded sensitivity" = "#BD6D61"
)
grid_col <- "#E5E7EB"
text_col <- "#111827"
subtle_col <- "#6B7280"

read_project_csv <- function(name) {
  read.csv(file.path(pkg, name), stringsAsFactors = FALSE, check.names = FALSE)
}

stability <- read_project_csv("additional_file_13_profile_stability_guardrails.csv")
robust <- read_project_csv("additional_file_17_gmm_algorithm_robustness.csv")
design <- read_project_csv("additional_file_12_baseline_clinical_design_covariate_availability.csv")
boot <- read.csv(file.path(root, "outputs/phase32_gmm_bootstrap_stability.csv"), stringsAsFactors = FALSE, check.names = FALSE)

phase47_boot_path <- file.path(root, "outputs/phase47_gmm_bootstrap_robustness_replicates.csv")
phase47_summary_path <- file.path(root, "outputs/phase47_gmm_bootstrap_robustness_summary.csv")
if (file.exists(phase47_boot_path) && file.exists(phase47_summary_path)) {
  boot <- read.csv(phase47_boot_path, stringsAsFactors = FALSE, check.names = FALSE)
  phase47_summary <- read.csv(phase47_summary_path, stringsAsFactors = FALSE, check.names = FALSE)
  phase47_summary <- phase47_summary[, c(
    "cohort",
    "median_ari_vs_reference",
    "p10_ari_vs_reference",
    "min_ari_vs_reference",
    "max_covariance_condition_number"
  )]
  stability <- merge(stability, phase47_summary, by = "cohort", all.x = TRUE, sort = FALSE)
  stability$bootstrap_median_ari <- ifelse(
    is.na(stability$median_ari_vs_reference),
    stability$bootstrap_median_ari,
    stability$median_ari_vs_reference
  )
  stability$bootstrap_p10_ari <- ifelse(
    is.na(stability$p10_ari_vs_reference),
    stability$bootstrap_p10_ari,
    stability$p10_ari_vs_reference
  )
  stability$bootstrap_min_ari <- ifelse(
    is.na(stability$min_ari_vs_reference),
    stability$bootstrap_min_ari,
    stability$min_ari_vs_reference
  )
  stability$max_covariance_condition_number <- ifelse(
    is.na(stability$max_covariance_condition_number.y),
    stability$max_covariance_condition_number.x,
    stability$max_covariance_condition_number.y
  )
  stability$max_covariance_condition_number.x <- NULL
  stability$max_covariance_condition_number.y <- NULL
}

stability <- stability[match(cohort_order, stability$cohort), ]
boot <- boot[boot$cohort %in% cohort_order & !is.na(boot$adjusted_rand_index_vs_reference), ]
boot$cohort <- factor(boot$cohort, levels = cohort_order)
robust <- robust[robust$cohort %in% cohort_order & robust$method %in% method_order, ]
robust$cohort <- factor(robust$cohort, levels = cohort_order)
robust$method <- factor(robust$method, levels = method_order)

mat <- matrix(NA_real_, nrow = length(cohort_order), ncol = length(method_order), dimnames = list(cohort_order, method_labels))
for (i in seq_len(nrow(robust))) {
  mat[as.character(robust$cohort[i]), method_labels[match(as.character(robust$method[i]), method_order)]] <- robust$ari_vs_selected_gmm[i]
}
write.table(data.frame(cohort = rownames(mat), mat, check.names = FALSE), file.path(tab_dir, "fig2B_complexheatmap_method_ari_input_mapped.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)
write.table(boot, file.path(tab_dir, "fig2A_raincloud_bootstrap_input_mapped.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)

stability$log10_condition <- log10(stability$max_covariance_condition_number)
write.table(stability[, c("cohort", "role", "bootstrap_median_ari", "algorithm_ari_median", "max_covariance_condition_number", "log10_condition")], file.path(tab_dir, "fig2C_radial_lollipop_condition_input_mapped.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)

decision <- merge(
  stability[, c("cohort", "role", "bootstrap_p10_ari", "bootstrap_median_ari", "algorithm_ari_median", "log10_condition")],
  design[, c("cohort", "complete_four_domain_n")],
  by = "cohort",
  all.x = TRUE
)
decision <- decision[match(cohort_order, decision$cohort), ]
decision$decision_region <- ifelse(
  decision$bootstrap_p10_ari >= 0.75 & decision$log10_condition < 6.0,
  "stable",
  ifelse(
    decision$bootstrap_p10_ari >= 0.75 & decision$log10_condition >= 6.0,
    "reproducible but near-singular",
    ifelse(decision$bootstrap_p10_ari < 0.75 & decision$log10_condition >= 6.0, "fragile and near-singular", "fragile")
  )
)
write.table(decision, file.path(tab_dir, "fig2D_stability_decision_quadrant_input_mapped.tsv"), sep = "\t", row.names = FALSE, quote = FALSE)

col_fun <- circlize::colorRamp2(c(0, 0.5, 1), c("#2166AC", "#F7F7F7", "#9E0142"))

native_x <- function(x) unit(x, "native")
native_y <- function(y) unit(y, "native")

panel_label <- function(label) {
  grid.text(label, x = unit(0.01, "npc"), y = unit(0.98, "npc"), just = c("left", "top"), gp = gpar(fontsize = 8, fontface = "bold", col = text_col))
}

draw_panel_a <- function() {
  panel_label("A")
  pushViewport(viewport(x = 0.07, y = 0.08, width = 0.90, height = 0.82, just = c("left", "bottom"), xscale = c(-0.16, 1), yscale = c(0.5, length(cohort_order) + 0.5), clip = "off"))
  grid.rect(x = native_x(0.25), width = native_x(0.50), gp = gpar(fill = "#F3F4F6", col = NA, alpha = 0.5), just = "left")
  grid.rect(x = native_x(0.50), width = native_x(0.30), gp = gpar(fill = "#FEF3C7", col = NA, alpha = 0.35), just = "left")
  grid.rect(x = native_x(0.80), width = native_x(0.20), gp = gpar(fill = "#ECFDF5", col = NA, alpha = 0.42), just = "left")
  for (xx in seq(0, 1, by = 0.25)) {
    grid.lines(x = native_x(c(xx, xx)), y = native_y(c(0.5, length(cohort_order) + 0.5)), gp = gpar(col = grid_col, lwd = 0.75))
  }
  for (i in seq_along(cohort_order)) {
    cohort <- cohort_order[i]
    y <- length(cohort_order) - i + 1
    vals <- boot$adjusted_rand_index_vs_reference[boot$cohort == cohort]
    role <- stability$role[stability$cohort == cohort]
    col <- tier_colors[role]
    if (length(vals) > 1 && length(unique(vals)) > 1) {
      den <- density(vals, from = 0, to = 1, n = 120, adjust = 0.85)
      scaled <- den$y / max(den$y) * 0.34
      grid.polygon(x = native_x(c(den$x, rev(den$x))), y = native_y(c(rep(y, length(den$x)), rev(y + scaled))), gp = gpar(fill = col, col = NA, alpha = 0.22))
      set.seed(100 + i)
      jit <- runif(length(vals), -0.06, 0.06)
      grid.points(x = native_x(vals), y = native_y(rep(y - 0.08, length(vals)) + jit), pch = 16, size = unit(1.6, "mm"), gp = gpar(col = col, alpha = 0.56))
    }
    q <- quantile(vals, probs = c(0.10, 0.50, 0.90), na.rm = TRUE)
    grid.lines(x = native_x(c(q[1], q[3])), y = native_y(c(y, y)), gp = gpar(col = col, lwd = 1.35, lineend = "round"))
    grid.points(x = native_x(q[2]), y = native_y(y), pch = 21, size = unit(4.2, "mm"), gp = gpar(fill = col, col = "white", lwd = 0.75))
    grid.text(cohort, x = native_x(-0.035), y = native_y(y), just = "right", gp = gpar(fontsize = 6.2, col = text_col))
  }
  grid.xaxis(at = seq(0, 1, by = 0.25), gp = gpar(fontsize = 6.2, col = text_col), main = FALSE)
  grid.text("Bootstrap ARI", x = unit(0.5, "npc"), y = unit(-0.12, "npc"), gp = gpar(fontsize = 7.5, col = text_col))
  grid.text("fragile", x = native_x(0.25), y = native_y(7.45), gp = gpar(fontsize = 5.3, col = subtle_col))
  grid.text("moderate", x = native_x(0.65), y = native_y(7.45), gp = gpar(fontsize = 5.3, col = subtle_col))
  grid.text("robust", x = native_x(0.90), y = native_y(7.45), gp = gpar(fontsize = 5.3, col = subtle_col))
  popViewport()
}

draw_panel_b <- function() {
  panel_label("B")
  pushViewport(viewport(x = 0.02, y = 0.02, width = 0.95, height = 0.90, just = c("left", "bottom")))
  row_roles <- stability$role[match(cohort_order, stability$cohort)]
  names(row_roles) <- cohort_order
  row_ha <- rowAnnotation(
    Tier = row_roles,
    col = list(Tier = tier_colors),
    show_annotation_name = FALSE,
    width = unit(3.0, "mm"),
    show_legend = FALSE
  )
  column_group <- factor(
    c("GMM", "GMM", "Cluster", "Cluster", "Score"),
    levels = c("GMM", "Cluster", "Score")
  )
  ht <- Heatmap(
    mat,
    name = "ARI",
    col = col_fun,
    cluster_rows = FALSE,
    cluster_columns = FALSE,
    column_split = column_group,
    column_gap = unit(1.2, "mm"),
    column_title_gp = gpar(fontsize = 5.4, fontface = "bold", col = subtle_col),
    column_title_rot = 0,
    show_heatmap_legend = FALSE,
    row_names_gp = gpar(fontsize = 6.2, col = text_col),
    column_names_gp = gpar(fontsize = 5.9, col = text_col),
    column_names_rot = 0,
    rect_gp = gpar(col = "#FFFFFF", lwd = 1.05),
    left_annotation = row_ha,
    cell_fun = function(j, i, x, y, width, height, fill) {
      value <- mat[i, j]
      if (!is.na(value)) {
        text_color <- ifelse(value >= 0.75 || value <= 0.18, "white", text_col)
        grid.text(sprintf("%.2f", value), x = x, y = y, gp = gpar(fontsize = 5.8, fontface = "bold", col = text_color))
        if (value < 0.30 && j != 1) {
          grid.rect(x = x, y = y, width = width * 0.86, height = height * 0.70, gp = gpar(fill = NA, col = "#374151", lwd = 0.55, lty = 3))
        }
        if (j == 1) {
          grid.rect(x = x, y = y, width = width * 0.94, height = height * 0.82, gp = gpar(fill = NA, col = "#111827", lwd = 1.0))
        }
      }
    }
  )
  draw(ht, newpage = FALSE, padding = unit(c(1, 1, 1, 1), "mm"))
  popViewport()
}

draw_panel_c <- function() {
  panel_label("C")
  ranked <- stability[order(stability$log10_condition, decreasing = TRUE), ]
  base_x <- 5.85
  pushViewport(viewport(
    x = 0.13, y = 0.10, width = 0.78, height = 0.78,
    just = c("left", "bottom"), xscale = c(base_x, 6.50),
    yscale = c(0.45, nrow(ranked) + 0.55), clip = "off"
  ))
  grid.rect(
    x = unit((6.00 + 6.50) / 2, "native"), y = unit((0.45 + nrow(ranked) + 0.55) / 2, "native"),
    width = unit(0.50, "native"), height = unit(nrow(ranked) + 0.10, "native"),
    gp = gpar(fill = "#FDECEC", col = NA, alpha = 0.55)
  )
  for (tick in c(5.9, 6.0, 6.2, 6.4)) {
    grid.lines(
      x = unit(c(tick, tick), "native"),
      y = unit(c(0.55, nrow(ranked) + 0.45), "native"),
      gp = gpar(col = ifelse(tick == 6.0, "#6B7280", grid_col), lwd = ifelse(tick == 6.0, 1.0, 0.5), lty = ifelse(tick == 6.0, 2, 1))
    )
    grid.text(sprintf("%.1f", tick), x = unit(tick, "native"), y = unit(0.20, "native"), gp = gpar(fontsize = 5.4, col = subtle_col))
  }
  for (i in seq_len(nrow(ranked))) {
    row <- ranked[i, ]
    y <- nrow(ranked) - i + 1
    col <- tier_colors[row$role]
    grid.rect(
      x = unit((base_x + row$log10_condition) / 2, "native"),
      y = unit(y, "native"),
      width = unit(max(row$log10_condition - base_x, 0.01), "native"),
      height = unit(0.46, "native"),
      gp = gpar(fill = col, col = NA, alpha = 0.92)
    )
    grid.points(x = unit(row$log10_condition, "native"), y = unit(y, "native"), pch = 21, size = unit(3.4, "mm"), gp = gpar(fill = col, col = "white", lwd = 0.75))
    grid.text(row$cohort, x = unit(base_x - 0.02, "native"), y = unit(y, "native"), just = "right", gp = gpar(fontsize = 5.9, col = text_col))
    grid.text(sprintf("%.2f", row$log10_condition), x = unit(row$log10_condition + 0.018, "native"), y = unit(y, "native"), just = "left", gp = gpar(fontsize = 5.5, col = text_col))
  }
  grid.lines(x = unit(c(base_x, 6.50), "native"), y = unit(c(0.55, 0.55), "native"), gp = gpar(col = text_col, lwd = 0.85))
  grid.text("near-singular threshold", x = unit(6.02, "native"), y = unit(nrow(ranked) + 0.62, "native"), just = "left", gp = gpar(fontsize = 5.5, col = subtle_col))
  grid.text("log10 covariance condition", x = unit((base_x + 6.50) / 2, "native"), y = unit(-0.18, "native"), gp = gpar(fontsize = 6.4, col = text_col))
  popViewport()
}

draw_panel_d <- function() {
  panel_label("D")
  pushViewport(viewport(x = 0.09, y = 0.09, width = 0.84, height = 0.80, just = c("left", "bottom"), xscale = c(0.18, 1.03), yscale = c(5.86, 6.48), clip = "off"))
  grid.rect(x = unit((0.18 + 0.75) / 2, "native"), y = unit((6.00 + 6.48) / 2, "native"), width = unit(0.75 - 0.18, "native"), height = unit(6.48 - 6.00, "native"), gp = gpar(fill = "#FDECEC", col = NA))
  grid.rect(x = unit((0.75 + 1.03) / 2, "native"), y = unit((6.00 + 6.48) / 2, "native"), width = unit(1.03 - 0.75, "native"), height = unit(6.48 - 6.00, "native"), gp = gpar(fill = "#FFF7DF", col = NA))
  grid.rect(x = unit((0.18 + 0.75) / 2, "native"), y = unit((5.86 + 6.00) / 2, "native"), width = unit(0.75 - 0.18, "native"), height = unit(6.00 - 5.86, "native"), gp = gpar(fill = "#F6F7F9", col = NA))
  grid.rect(x = unit((0.75 + 1.03) / 2, "native"), y = unit((5.86 + 6.00) / 2, "native"), width = unit(1.03 - 0.75, "native"), height = unit(6.00 - 5.86, "native"), gp = gpar(fill = "#EAF6F2", col = NA))
  for (xv in c(0.25, 0.50, 0.75, 1.00)) {
    grid.lines(x = unit(c(xv, xv), "native"), y = unit(c(5.86, 6.48), "native"), gp = gpar(col = grid_col, lwd = 0.45))
  }
  for (yv in c(5.9, 6.0, 6.2, 6.4)) {
    grid.lines(x = unit(c(0.18, 1.03), "native"), y = unit(c(yv, yv), "native"), gp = gpar(col = grid_col, lwd = 0.45))
  }
  grid.lines(x = unit(c(0.75, 0.75), "native"), y = unit(c(5.86, 6.48), "native"), gp = gpar(col = "#6B7280", lwd = 0.90, lty = 2))
  grid.lines(x = unit(c(0.18, 1.03), "native"), y = unit(c(6.00, 6.00), "native"), gp = gpar(col = "#6B7280", lwd = 0.90, lty = 2))
  grid.lines(x = unit(c(0.18, 1.03), "native"), y = unit(c(5.86, 5.86), "native"), gp = gpar(col = text_col, lwd = 0.95))
  grid.lines(x = unit(c(0.18, 0.18), "native"), y = unit(c(5.86, 6.48), "native"), gp = gpar(col = text_col, lwd = 0.95))
  grid.text("fragile +\nnear-singular", x = unit(0.36, "native"), y = unit(6.40, "native"), gp = gpar(fontsize = 5.3, col = subtle_col))
  grid.text("reproducible +\nnear-singular", x = unit(0.94, "native"), y = unit(6.37, "native"), gp = gpar(fontsize = 5.3, col = subtle_col))
  grid.text("lower\nconcern", x = unit(0.90, "native"), y = unit(5.92, "native"), gp = gpar(fontsize = 5.3, col = subtle_col))
  grid.text("Bootstrap p10 ARI", x = unit(0.60, "native"), y = unit(5.885, "native"), gp = gpar(fontsize = 6.2, col = text_col))
  grid.text("log10 covariance condition", x = unit(-0.10, "npc"), y = unit(0.52, "npc"), rot = 90, gp = gpar(fontsize = 6.2, col = text_col))
  for (tick in c(0.25, 0.50, 0.75, 1.00)) {
    grid.text(sprintf("%.2g", tick), x = unit(tick, "native"), y = unit(5.83, "native"), gp = gpar(fontsize = 5.4, col = subtle_col))
  }
  grid.text("6.0", x = unit(0.155, "native"), y = unit(6.00, "native"), gp = gpar(fontsize = 5.4, col = subtle_col), just = "right")

  max_n <- max(decision$complete_four_domain_n, na.rm = TRUE)
  label_offsets <- list(
    "CHARLS" = c(-0.050, 0.070),
    "ELSA" = c(-0.080, 0.040),
    "HRS" = c(-0.040, 0.065),
    "KLoSA" = c(0.055, -0.065),
    "LASI" = c(-0.070, -0.085),
    "MHAS" = c(-0.100, -0.060),
    "SHARE" = c(0.022, -0.035)
  )
  for (i in seq_len(nrow(decision))) {
    row <- decision[i, ]
    col <- tier_colors[row$role]
    size_mm <- 2.8 + 2.25 * sqrt(row$complete_four_domain_n / max_n)
    x <- row$bootstrap_p10_ari
    y <- row$log10_condition
    grid.points(x = unit(x, "native"), y = unit(y, "native"), pch = 21, size = unit(size_mm, "mm"), gp = gpar(fill = col, col = "white", lwd = 0.85))
    if (!is.na(row$algorithm_ari_median) && row$algorithm_ari_median >= 0.50) {
      grid.points(x = unit(x, "native"), y = unit(y, "native"), pch = 1, size = unit(size_mm + 1.1, "mm"), gp = gpar(col = text_col, lwd = 0.75))
    }
    off <- label_offsets[[row$cohort]]
    lx <- min(max(x + off[1], 0.20), 1.00)
    ly <- min(max(y + off[2], 5.89), 6.45)
    grid.lines(x = unit(c(x, lx), "native"), y = unit(c(y, ly), "native"), gp = gpar(col = col, lwd = 0.55, alpha = 0.80))
    grid.text(row$cohort, x = unit(lx, "native"), y = unit(ly, "native"), gp = gpar(fontsize = 5.3, col = text_col), just = ifelse(off[1] < 0, "right", "left"))
  }
  grid.text("point size = complete four-domain N; outer ring = algorithm ARI median >=0.50", x = unit(0.62, "native"), y = unit(6.51, "native"), gp = gpar(fontsize = 5.1, col = subtle_col))
  popViewport()
}

draw_figure <- function() {
  grid.newpage()
  pushViewport(viewport(width = unit(1, "npc"), height = unit(1, "npc")))
  pushViewport(viewport(layout = grid.layout(
    nrow = 2, ncol = 2,
    widths = unit(c(0.50, 0.50), "npc"),
    heights = unit(c(0.52, 0.48), "npc")
  )))
  pushViewport(viewport(layout.pos.row = 1, layout.pos.col = 1)); draw_panel_a(); popViewport()
  pushViewport(viewport(layout.pos.row = 1, layout.pos.col = 2)); draw_panel_b(); popViewport()
  pushViewport(viewport(layout.pos.row = 2, layout.pos.col = 1)); draw_panel_c(); popViewport()
  pushViewport(viewport(layout.pos.row = 2, layout.pos.col = 2)); draw_panel_d(); popViewport()
  popViewport(2)
}

width_in <- 180 / 25.4
height_in <- 160 / 25.4
out_base <- "figure2_enhanced_complexheatmap_radial_decision_phase49"
legacy_base <- "figure2_enhanced_complexheatmap_radial_hf147_phase49"
svg(file.path(out_dir, paste0(out_base, ".svg")), width = width_in, height = height_in, family = "Arial")
draw_figure()
dev.off()
# The base PDF device may not know the Arial family even when SVG text can
# retain an Arial declaration. Use the closest built-in sans fallback for PDF.
pdf(file.path(out_dir, paste0(out_base, ".pdf")), width = width_in, height = height_in, family = "Helvetica", useDingbats = FALSE)
draw_figure()
dev.off()
png(file.path(out_dir, paste0(out_base, ".png")), width = width_in, height = height_in, units = "in", res = 300)
draw_figure()
dev.off()

for (ext in c("svg", "pdf", "png")) {
  file.copy(file.path(out_dir, paste0(out_base, ".", ext)), file.path(out_dir, paste0(legacy_base, ".", ext)), overwrite = TRUE)
}

cat(file.path(out_dir, paste0(out_base, ".svg")), "\n")
