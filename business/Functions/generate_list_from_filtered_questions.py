import barcode
import os
import requests
from PIL import Image

from barcode.writer import ImageWriter
from business.Classes.PDF_Generator import PDF_Generator
from business.Functions.generate_link_to_youtube import generate_link_to_youtube
from business.Functions.remove_invalid_characters import remove_invalid_characters


def generate_list_from_filtered_questions(dfResult_CN, Habilidade, flashname):

    pdf = PDF_Generator()
    pdf.alias_nb_pages()
    pdf.set_title(flashname)

    pdf.add_page()
    pdf.image("images/design/wordcloud_a4.png", x=0, y=0, w=pdf.w, h=pdf.h, type='png')
    pdf.add_page()

    pdf.set_font('Times', 'B', 12)
    img_dir = 'images/questions_images'  # Diretório local para salvar as imagens

    # Criar diretório se não existir
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    for i in dfResult_CN.index:
        print("N"+str(dfResult_CN.loc[i, 'indexacao'])+"/"+str(len(dfResult_CN)))
        strCN ="N"+str(dfResult_CN.loc[i, 'indexacao'])+" - Q" + str(dfResult_CN.loc[i, "CO_POSICAO"])+':'+str(dfResult_CN.loc[i, "ANO"]) + ' - H'+str(dfResult_CN.loc[i, "CO_HABILIDADE"].astype(int))+ " - Proficiência: " + str(dfResult_CN.loc[i, "theta_065"].round(2))
        
        if 'dtype:' in strCN:
            print("...")
        else:
            try:
                pdf.ln(15)  # adicionar espaço entre o texto e a imagem
                
                img_filename = f"{dfResult_CN.loc[i, 'CO_ITEM']}.png"
                img_path = os.path.join(img_dir, img_filename)

                codestr = f"{dfResult_CN.loc[i, 'CO_ITEM']}"

                img_pathax = os.path.join(img_dir, str('xa'+codestr))

                code128 = barcode.get("code128", codestr, writer=ImageWriter())
                filename = code128.save(img_pathax)
                img_pathax = img_pathax+'.png'

                # Verificar se a imagem já foi baixada
                if not os.path.exists(img_path):
                    url = 'https://niedsonemanoel.com.br/enem/An%C3%A1lise%20de%20Itens/OrdenarPorTri/1.%20Itens%20BNI_/'+ str(dfResult_CN.loc[i, "CO_ITEM"]) + '.png'
                    response = requests.get(url)

                    with open(img_path, 'wb') as img_file:
                        img_file.write(response.content)
                        print(img_path)

                # Abrir a imagem do diretório local
                with Image.open(img_path) as img:
                    img.thumbnail((160, 160))
                    width, height = img.size

                pdf.set_fill_color(255, 112, 79)
                #  pdf.ln(15)
                pdf.cell(0, 10, strCN, 0, 1, 'C', 1)
                pdf.ln(10)   # adicionar espaço entre o texto e a imagem

                # caCNular a posição y para centralizar a imagem
                y = pdf.get_y()

                # ajustar as coordenadas de posição e o tamanho da imagem
                pdf.image(img_path, x=pdf.w / 2 - width / 2, y=y, w=width, h=height)
                pdf.image(img_pathax, x=3, y=-3,  h=25) #w=45,
                pdf.ln(10)

                link = generate_link_to_youtube(remove_invalid_characters(dfResult_CN.loc[i, "OCRSearch"]))
                pdf.add_my_link(170, 25, "RESOLUÇÃO", link)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font('Times', 'B', 12)

                # adicionar quebra de página
                pdf.add_page()

            except FileNotFoundError:
                print(strCN)

                continue
    
    page_width = 190
    cell_width = 19
    max_cols = int(page_width / cell_width)

    # Junta as colunas do dataframe
    dfResult_CN['merged'] = dfResult_CN['indexacao'].astype(str) + ' - ' + dfResult_CN['TX_GABARITO']

    # Divide os dados em grupos de até max_cols colunas
    data = [dfResult_CN['merged'][i:i+max_cols].tolist() for i in range(0, len(dfResult_CN), max_cols)]

    # CaCNula a largura das células de acordo com o número de colunas
    cell_width = page_width / max_cols

    # Cria a tabela
    pdf.set_fill_color(89, 162, 165)
    # Title
    pdf.ln(15)
    pdf.cell(0, 10, str('GABARITO '+flashname.upper()), 0, 1, 'C', 1)
    pdf.ln(10)
    pdf.set_font('Arial', 'B', 12)

    for row in data:
        for col in row:
            pdf.cell(cell_width, 10, col, 1, 0, 'C')
        pdf.ln() # quebra de linha para a próxima linha da tabela

    pdf.ln(5)
    pdf.set_font('Arial', 'BI', 8)

    strOut = 'H'+str(Habilidade)+'_'+str(flashname)+ '.pdf'

    pdf.output(strOut, 'F')

    return 'H'+str(Habilidade)+'_'+str(flashname)
