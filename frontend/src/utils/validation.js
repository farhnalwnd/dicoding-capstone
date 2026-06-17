/**
 * Validation utilities for file uploads and text inputs.
 */

/**
 * Validates a single file against format and size constraints.
 * 
 * @param {File} file - The file object to validate
 * @param {Array<string>} allowedExtensions - Array of lowercase extensions (e.g. ['pdf', 'docx'])
 * @param {number} maxSizeMB - Maximum allowed file size in MB (default 10MB)
 * @returns {Object} Validation result { valid: boolean, error: string|null }
 */
export const validateFile = (file, allowedExtensions = ['pdf', 'docx'], maxSizeMB = 10) => {
  if (!file) {
    return { valid: false, error: 'Please upload a file.' }
  }

  const filename = file.name || ''
  const extension = filename.split('.').pop().toLowerCase()

  if (!allowedExtensions.includes(extension)) {
    return {
      valid: false,
      error: 'Unsupported file format. Please upload PDF or DOCX.'
    }
  }

  const maxSizeBytes = maxSizeMB * 1024 * 1024
  if (file.size > maxSizeBytes) {
    return {
      valid: false,
      error: `File exceeds maximum allowed size of ${maxSizeMB}MB.`
    }
  }

  return { valid: true, error: null }
}

/**
 * Validates an array of files.
 * 
 * @param {FileList|Array<File>} files - File list or array to validate
 * @param {Array<string>} allowedExtensions - Allowed extensions
 * @param {number} maxSizeMB - Max file size in MB
 * @returns {Object} Validation result
 */
export const validateMultipleFiles = (files, allowedExtensions = ['pdf', 'docx'], maxSizeMB = 10) => {
  if (!files || !files.length) {
    return { valid: false, error: 'Please upload at least one file.' }
  }

  for (let i = 0; i < files.length; i++) {
    const fileValidation = validateFile(files[i], allowedExtensions, maxSizeMB)
    if (!fileValidation.valid) {
      return {
        valid: false,
        error: `File "${files[i].name}": ${fileValidation.error}`
      }
    }
  }

  return { valid: true, error: null }
}
