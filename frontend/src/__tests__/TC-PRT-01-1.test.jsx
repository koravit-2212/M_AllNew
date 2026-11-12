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

test('test_TC_PRT_01_1_bw_cost_preview', async () => {
  // Given นักศึกษาเลือกไฟล์ report.pdf และเลือกชนิดขาว-ดำ
  const client = makeClient()
  render(<PrintPage client={client} />)
  await pickFile()
  await screen.findByText('report.pdf (1.2 MB)')

  // When กำหนดจำนวนหน้า 12 และจำนวนชุด 2
  await setAmounts(12, 2)

  // Then (1) แสดงตัวเลือกชนิดการพิมพ์ ขาว-ดำ และสี
  expect(screen.getByLabelText('ขาว-ดำ').checked).toBe(true)
  expect(screen.getByLabelText('สี')).toBeTruthy()
  // (5) หน้าจอแสดงบรรทัดคำนวณและค่าใช้บริการ
  const cost = within(screen.getByLabelText('ค่าใช้บริการ'))
  expect(cost.getByText('12 หน้า × 2 ชุด = 24 หน้า')).toBeTruthy()
  expect(cost.getByText(`${24 * RATES.BW} บาท`)).toBeTruthy()
  // (4) ยังไม่มีการส่งงาน
  expect(client.submitPrintJob).not.toHaveBeenCalled()
})
