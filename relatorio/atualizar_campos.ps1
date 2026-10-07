# Abre o relatório no Word, atualiza sumário, listas e numeração das
# legendas, salva e exporta o PDF ao lado do .docx.
#
# Uso:  powershell -ExecutionPolicy Bypass -File relatorio\atualizar_campos.ps1

$docx = Join-Path $PSScriptRoot "Relatorio_Final_PIBIC_BioquimicaEDU.docx"
$pdf = [IO.Path]::ChangeExtension($docx, ".pdf")

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$word.DisplayAlerts = 0
try {
    $doc = $word.Documents.Open($docx)
    # duas passadas: preencher o sumário e as listas desloca páginas
    foreach ($passada in 1..2) {
        $doc.Fields.Update() | Out-Null
        foreach ($t in $doc.TablesOfContents) { $t.Update() }
        foreach ($t in $doc.TablesOfFigures) { $t.Update() }
        $doc.Repaginate()
    }
    $doc.Save()
    $doc.ExportAsFixedFormat($pdf, 17)   # 17 = PDF
    Write-Output "paginas: $($doc.ComputeStatistics(2))"
    $doc.Close()
    Write-Output "atualizado: $docx"
    Write-Output "pdf: $pdf"
}
finally {
    $word.Quit()
    [System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null
}
