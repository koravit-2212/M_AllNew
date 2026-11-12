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

test('test_TC_PRT_03_1_offline_not_sent', async () => {
  // Given เครื่องพิมพ์สถานะ offline (หลังบ้านตอบ 409) และเลือกไฟล์ที่รองรับแล้ว
  const client = makeClient({ submitPrintJob: vi.fn().mockRejectedValue(Object.assign(new Error('Print submit failed: 409'), { status: 409 })) })
  render(<PrintPage client={client} />)
  await pickFile()
  await screen.findByText('report.pdf (1.2 MB)')
  await setAmounts(5, 1)
  fireEvent.click(screen.getByRole('button', { name: 'ถัดไป' }))

  // When นักศึกษายืนยันการพิมพ์
  fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการพิมพ์' }))

  // Then (4) หน้าจอแสดงเครื่องพิมพ์ไม่พร้อมใช้งาน และมีปุ่มลองใหม่
  expect(await screen.findByText('เครื่องพิมพ์ไม่พร้อมใช้งาน')).toBeTruthy()
  expect(screen.getByRole('button', { name: 'ลองใหม่' })).toBeTruthy()
  expect(screen.queryByText('ส่งงานพิมพ์แล้ว')).toBeNull()
  // ((1)-(3) ตรวจด้วย pytest)
})
