// T-04 (FR-PRT-01, FR-PRT-02, NFR-USB-01) ตรวจด้วย AC-PRT-01
// T-06 (FR-PRT-03, NFR-USB-01) ตรวจด้วย AC-PRT-02
// T-08 (FR-PRT-05, NFR-USB-01) ตรวจด้วย AC-PRT-03
import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { vi } from 'vitest'

import PrintPage from '../pages/PrintPage.jsx'

const MODES = [
  { code: 'BW', label: 'ขาว-ดำ', rate_per_page: 1 },
  { code: 'Color', label: 'สี', rate_per_page: 5 },
]

function makeClient(submitPrintJob = vi.fn().mockResolvedValue({ printjob_id: 'JOB-0001', status: 'sent', filename: 'report.pdf', total_pages: 24, total_cost: 24 })) {
  return {
    submitPrintJob,
    uploadPrintFile: vi.fn().mockResolvedValue({ file_id: 'FILE-0001', filename: 'report.pdf', size_bytes: 1258291, pages_detected: null }),
    getPrintOptions: vi.fn().mockImplementation(async ({ pages, copies, colorMode }) => ({
      file_id: 'FILE-0001',
      pages,
      copies,
      color_mode: colorMode,
      allowed_color_modes: MODES,
      total_pages: pages * copies,
      estimated_cost: pages * copies * (colorMode === 'Color' ? 5 : 1),
    })),
  }
}

async function chooseFile(name = 'report.pdf', size = 1258291, type = 'application/pdf') {
  const file = new File(['x'], name, { type })
  Object.defineProperty(file, 'size', { value: size })
  fireEvent.change(screen.getByLabelText('ไฟล์'), { target: { files: [file] } })
}

describe('AC-PRT-01 เห็นตัวเลือกการพิมพ์และค่าใช้บริการก่อนยืนยัน', () => {
  it('AC-PRT-01 เลือกไฟล์ กรอก 12 หน้า 2 ชุด แล้วเห็นบรรทัดคำนวณและค่าใช้บริการ', async () => {
    // Given นักศึกษาเลือกไฟล์ที่รองรับ
    const client = makeClient()
    render(<PrintPage client={client} />)
    await chooseFile()
    expect(await screen.findByText('report.pdf (1.2 MB)')).toBeTruthy()

    // When นักศึกษากำหนดจำนวนหน้าและจำนวนชุด
    fireEvent.change(screen.getByLabelText('จำนวนหน้า'), { target: { value: '12' } })
    fireEvent.change(screen.getByLabelText('จำนวนชุด'), { target: { value: '2' } })

    // Then ระบบแสดงตัวเลือกการพิมพ์และค่าใช้บริการที่คำนวณถูกต้องก่อนให้ยืนยัน
    const cost = within(await screen.findByLabelText('ค่าใช้บริการ'))
    await waitFor(() => expect(cost.getByText('12 หน้า × 2 ชุด = 24 หน้า')).toBeTruthy())
    expect(cost.getByText('24 บาท')).toBeTruthy()
    expect(screen.getByLabelText('ขาว-ดำ')).toBeTruthy()
    fireEvent.click(screen.getByLabelText('สี'))
    await waitFor(() => expect(cost.getByText('120 บาท')).toBeTruthy())
    expect(client.uploadPrintFile).toHaveBeenCalledWith({ filename: 'report.pdf', contentType: 'application/pdf', sizeBytes: 1258291 })
  })
})

async function goToConfirm(client) {
  render(<PrintPage client={client} />)
  await chooseFile()
  await screen.findByText('report.pdf (1.2 MB)')
  fireEvent.change(screen.getByLabelText('จำนวนหน้า'), { target: { value: '12' } })
  fireEvent.change(screen.getByLabelText('จำนวนชุด'), { target: { value: '2' } })
  await waitFor(() => expect(screen.getByText('12 หน้า × 2 ชุด = 24 หน้า')).toBeTruthy())
  fireEvent.click(screen.getByRole('button', { name: 'ถัดไป' }))
}

describe('AC-PRT-02 ส่งงานพิมพ์สำเร็จ', () => {
  it('AC-PRT-02 กดยืนยันแล้วเห็นส่งงานพิมพ์แล้ว พร้อมชื่อไฟล์ จำนวนหน้ารวม และค่าใช้บริการ', async () => {
    // Given เครื่องปริ้นพร้อมใช้งานและไฟล์รองรับ
    const client = makeClient()
    await goToConfirm(client)

    // When นักศึกษายืนยันการพิมพ์
    fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการพิมพ์' }))

    // Then ระบบส่งงานไปยังเครื่องปริ้น
    await waitFor(() => expect(client.submitPrintJob).toHaveBeenCalledWith({ fileId: 'FILE-0001', pages: 12, copies: 2, colorMode: 'BW' }))
    expect(await screen.findByText('ส่งงานพิมพ์แล้ว')).toBeTruthy()
    expect(screen.getByText('บันทึกข้อมูลการใช้บริการแล้ว')).toBeTruthy()
    const card = within(screen.getByLabelText('งานพิมพ์'))
    expect(card.getByText('report.pdf')).toBeTruthy()
    expect(card.getByText('24 หน้า')).toBeTruthy()
    expect(card.getByText('24 บาท')).toBeTruthy()
  })

  it('AC-PRT-02 เหตุอื่น (เช่น เน็ตหลุด) เห็นส่งงานพิมพ์ไม่สำเร็จ กรุณาลองใหม่ (Q-09)', async () => {
    const client = makeClient(vi.fn().mockRejectedValue(new TypeError('Failed to fetch')))
    await goToConfirm(client)
    fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการพิมพ์' }))
    expect(await screen.findByText('ส่งงานพิมพ์ไม่สำเร็จ กรุณาลองใหม่')).toBeTruthy()
    expect(screen.queryByText('ส่งงานพิมพ์แล้ว')).toBeNull()
  })
})

describe('AC-PRT-03 เครื่องพิมพ์ไม่พร้อมใช้งาน', () => {
  it('AC-PRT-03 ยืนยันแล้วหลังบ้านตอบ 409 เห็นเครื่องพิมพ์ไม่พร้อมใช้งาน และกดลองใหม่ได้', async () => {
    // Given เครื่องปริ้นไม่พร้อมใช้งาน (ครั้งแรก) แล้วพร้อม (ครั้งที่สอง)
    const submitPrintJob = vi
      .fn()
      .mockRejectedValueOnce(Object.assign(new Error('Print submit failed: 409'), { status: 409 }))
      .mockResolvedValueOnce({ printjob_id: 'JOB-0001', status: 'sent', filename: 'report.pdf', total_pages: 24, total_cost: 24 })
    const client = makeClient(submitPrintJob)
    await goToConfirm(client)

    // When นักศึกษายืนยันการพิมพ์
    fireEvent.click(screen.getByRole('button', { name: 'ยืนยันการพิมพ์' }))

    // Then ระบบแจ้งเตือนผู้ใช้และไม่ส่งงานพิมพ์
    expect(await screen.findByText('เครื่องพิมพ์ไม่พร้อมใช้งาน')).toBeTruthy()
    expect(screen.getByText('ยังไม่ได้ส่งงานพิมพ์ กรุณาลองใหม่หรือติดต่อเจ้าหน้าที่')).toBeTruthy()
    expect(screen.queryByText('ส่งงานพิมพ์แล้ว')).toBeNull()

    fireEvent.click(screen.getByRole('button', { name: 'ลองใหม่' }))
    expect(await screen.findByText('ส่งงานพิมพ์แล้ว')).toBeTruthy()
    expect(submitPrintJob).toHaveBeenCalledTimes(2)
  })
})
