import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { vi } from 'vitest'

import PrintPage from '../pages/PrintPage.jsx'

// test จาก specs/006-printing/test-cases.md ห้ามแก้ให้ผ่าน
const RATES = { BW: 1, Color: 5 }
const MODES = [
  { code: 'BW', label: 'ขาว-ดำ', rate_per_page: RATES.BW },
  { code: 'Color', label: 'สี', rate_per_page: RATES.Color },
]

function makeClient(overrides = {}) {
  return {
    uploadPrintFile: vi.fn().mockImplementation(async ({ filename, sizeBytes }) => ({ file_id: 'FILE-0001', filename, size_bytes: sizeBytes, pages_detected: null })),
    getPrintOptions: vi.fn().mockImplementation(async ({ pages, copies, colorMode }) => ({
      file_id: 'FILE-0001',
      pages,
      copies,
      color_mode: colorMode,
      allowed_color_modes: MODES,
      total_pages: pages * copies,
      estimated_cost: pages * copies * RATES[colorMode],
    })),
    submitPrintJob: vi.fn().mockImplementation(async ({ pages, copies, colorMode }) => ({
      printjob_id: 'JOB-0001',
      status: 'sent',
      filename: 'report.pdf',
      total_pages: pages * copies,
      total_cost: pages * copies * RATES[colorMode],
    })),
    ...overrides,
  }
}

async function pickFile(name = 'report.pdf', size = 1258291, type = 'application/pdf') {
  const file = new File(['x'], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  fireEvent.change(screen.getByLabelText('ไฟล์'), { target: { files: [file] } })
}

async function setAmounts(pages, copies) {
  fireEvent.change(screen.getByLabelText('จำนวนหน้า'), { target: { value: String(pages) } })
  fireEvent.change(screen.getByLabelText('จำนวนชุด'), { target: { value: String(copies) } })
  await waitFor(() => expect(screen.getByText(`${pages} หน้า × ${copies} ชุด = ${pages * copies} หน้า`)).toBeTruthy())
}

test('test_TC_PRT_04_1_exe_rejected', async () => {
  // Given ไฟล์ setup.exe (หลังบ้านตอบ 415)
  const client = makeClient({
    uploadPrintFile: vi.fn().mockRejectedValue(
      Object.assign(new Error('Print upload failed: 415'), {
        status: 415,
        detail: { message: 'ไม่รองรับไฟล์ชนิดนี้', allowed_extensions: ['pdf', 'docx', 'pptx', 'xlsx', 'jpg', 'png'], max_size_mb: 50 },
      }),
    ),
  })
  render(<PrintPage client={client} />)

  // When นักศึกษาเลือกไฟล์
  await pickFile('setup.exe', 1000, 'application/octet-stream')

  // Then (3) หน้าจอแสดงคำเตือน และปุ่มถัดไปกดไม่ได้
  expect(await screen.findByText('ไม่รองรับไฟล์ชนิดนี้')).toBeTruthy()
  expect(screen.getByText(/\.pdf, \.docx, \.pptx, \.xlsx, \.jpg, \.png ขนาดไม่เกิน 50 MB/)).toBeTruthy()
  expect(screen.getByRole('button', { name: 'ถัดไป' }).disabled).toBe(true)
  // ((1)(2) ตรวจด้วย pytest)
})
